import os
import tempfile

from tools.filesystem import write_file, read_file, search_files, create_folder, delete_file


def test_write_and_read_file_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "notes.txt")
        content = "hello from local test"

        w = write_file.invoke({"path": target, "content": content})
        assert "✅" in w

        r = read_file.invoke(target)
        assert "hello from local test" in r


def test_search_files_finds_pattern():
    with tempfile.TemporaryDirectory() as tmp:
        create_folder.invoke(os.path.join(tmp, "sub"))
        write_file.invoke({"path": os.path.join(tmp, "a.txt"), "content": "a"})
        write_file.invoke({"path": os.path.join(tmp, "sub", "b.txt"), "content": "b"})
        write_file.invoke({"path": os.path.join(tmp, "sub", "c.log"), "content": "c"})

        out = search_files.invoke({"root_path": tmp, "pattern": "*.txt"})
        assert "Found" in out
        assert "a.txt" in out
        assert "b.txt" in out
        assert "c.log" not in out


def test_delete_file_and_folder():
    with tempfile.TemporaryDirectory() as tmp:
        folder = os.path.join(tmp, "to_delete")
        create_folder.invoke(folder)
        file_path = os.path.join(folder, "x.txt")
        write_file.invoke({"path": file_path, "content": "x"})

        d1 = delete_file.invoke(file_path)
        assert "✅" in d1
        assert not os.path.exists(file_path)

        d2 = delete_file.invoke(folder)
        assert "✅" in d2
        assert not os.path.exists(folder)
