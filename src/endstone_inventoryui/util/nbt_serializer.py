from __future__ import annotations

from enum import IntEnum
from typing import Union

from endstone.nbt import *
from bstream import BinaryStream, ReadOnlyBinaryStream


__all__ = ["write_nbt", "read_nbt", "NBTError"]


class NBTError(ValueError):
    """Raised for malformed data or tags that can't be represented."""


class TagId(IntEnum):
    END = 0
    BYTE = 1
    SHORT = 2
    INT = 3
    LONG = 4
    FLOAT = 5
    DOUBLE = 6
    BYTE_ARRAY = 7
    STRING = 8
    LIST = 9
    COMPOUND = 10
    INT_ARRAY = 11


_TYPE_TO_ID = {
    ByteTag: TagId.BYTE,
    ShortTag: TagId.SHORT,
    IntTag: TagId.INT,
    LongTag: TagId.LONG,
    FloatTag: TagId.FLOAT,
    DoubleTag: TagId.DOUBLE,
    ByteArrayTag: TagId.BYTE_ARRAY,
    StringTag: TagId.STRING,
    ListTag: TagId.LIST,
    CompoundTag: TagId.COMPOUND,
    IntArrayTag: TagId.INT_ARRAY,
}


def _tag_id(tag: Tag) -> TagId:
    try:
        return _TYPE_TO_ID[type(tag)]
    except KeyError:
        raise NBTError(f"Unsupported tag type: {type(tag)!r}") from None


def _to_signed_byte(value: int) -> int:
    """Convert a raw 0-255 byte into NBT's signed (-128..127) domain."""
    return value - 256 if value >= 128 else value


# --------------------------------------------------------------------------
# Writing
# --------------------------------------------------------------------------

def _write_payload(stream: BinaryStream, tag: Tag) -> None:
    match tag:
        case ByteTag():
            stream.write_byte(tag.value & 0xFF)

        case ShortTag():
            stream.write_signed_short(tag.value)

        case IntTag():
            stream.write_signed_int(tag.value)

        case LongTag():
            stream.write_signed_int64(tag.value)

        case FloatTag():
            stream.write_float(tag.value)

        case DoubleTag():
            stream.write_double(tag.value)

        case StringTag():
            stream.write_short_string(tag.value)

        case ByteArrayTag():
            stream.write_signed_int(len(tag))
            stream.write_raw_bytes(bytes(int(v) & 0xFF for v in tag))

        case IntArrayTag():
            stream.write_signed_int(len(tag))
            for v in tag:
                stream.write_signed_int(int(v))

        case ListTag():
            if len(tag) == 0:
                stream.write_byte(TagId.END)
                stream.write_signed_int(0)
                return

            element_id = _tag_id(tag[0])

            for element in tag:
                if _tag_id(element) != element_id:
                    raise NBTError(
                        "ListTag elements must all share the same tag type"
                    )

            stream.write_byte(element_id)
            stream.write_signed_int(len(tag))

            for element in tag:
                _write_payload(stream, element)
        case CompoundTag():
            for key, value in tag.items():
                stream.write_byte(_tag_id(value))
                stream.write_short_string(key)
                _write_payload(stream, value)

            stream.write_byte(TagId.END)
        case _:
            raise NBTError(f"Unsupported tag type: {type(tag)!r}")


def write_nbt(tag: Tag, name: str = "") -> bytes:
    """
    Serialize an NBT tag with little-endian.

    :param tag: The root tag.
    :param name: The root tag's name.
    :return: Raw serialized NBT bytes.
    """

    stream = BinaryStream()

    stream.write_byte(_tag_id(tag))
    stream.write_short_string(name)
    _write_payload(stream, tag)

    return stream.get_and_release_data()


# --------------------------------------------------------------------------
# Reading
# --------------------------------------------------------------------------

def _read_payload(reader: ReadOnlyBinaryStream, tag_id: int) -> Tag:
    match tag_id:
        case TagId.BYTE:
            return ByteTag(_to_signed_byte(reader.get_byte()))

        case TagId.SHORT:
            return ShortTag(reader.get_signed_short())

        case TagId.INT:
            return IntTag(reader.get_signed_int())

        case TagId.LONG:
            return LongTag(reader.get_signed_int64())

        case TagId.FLOAT:
            return FloatTag(reader.get_float())

        case TagId.DOUBLE:
            return DoubleTag(reader.get_double())

        case TagId.BYTE_ARRAY:
            length = reader.get_signed_int()
            raw = reader.get_raw_bytes(length)

            return ByteArrayTag([
                _to_signed_byte(b)
                for b in raw
            ])

        case TagId.STRING:
            return StringTag(reader.get_short_string())

        case TagId.LIST:
            element_id = reader.get_byte()
            length = reader.get_signed_int()

            return ListTag([
                _read_payload(reader, element_id)
                for _ in range(length)
            ])

        case TagId.COMPOUND:
            compound = CompoundTag()

            while True:
                child_id = reader.get_byte()

                if child_id == TagId.END:
                    break

                key = reader.get_short_string()
                compound[key] = _read_payload(reader, child_id)

            return compound

        case TagId.INT_ARRAY:
            length = reader.get_signed_int()

            return IntArrayTag([
                reader.get_signed_int()
                for _ in range(length)
            ])

        case _:
            raise NBTError(f"Unknown tag id: {tag_id}")


def read_nbt(
    data: Union[bytes, bytearray, memoryview]
) -> tuple[str, Tag]:
    """
    Parse little-endian NBT.

    :param data: Raw serialized NBT bytes.
    :return: A tuple of (root_name, root_tag).
    """

    reader = ReadOnlyBinaryStream(bytes(data))

    tag_id = reader.get_byte()

    if tag_id == TagId.END:
        raise NBTError("No data: got TAG_End as the root tag")

    name = reader.get_short_string()
    tag = _read_payload(reader, tag_id)

    return name, tag