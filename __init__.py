import fire
import os
import sys

global global_targetpath


def bit_flip_bytes(bytes_data):
    # 对字节数组进行位反转
    return bytes(byte ^ 0xFF for byte in bytes_data)


def _obfuscate_header(input_file: str, noback: bool = False, minimum_size: int = 1024*1024):
    # 计算头部大小为文件的1%，但不少于1MB
    file_size = os.path.getsize(input_file)
    encrypt_size = max(int(file_size * 0.01), minimum_size)
    if file_size < minimum_size:  # 如果文件小于1MB，则混淆整个文件
        encrypt_size = file_size

    backup_file = input_file + ".headerbak"
    if os.path.exists(backup_file):
        print("错误: 检测到头部备份文件存在，无法继续执行。请确认上次操作是否成功，或手动删除备份文件。")
        sys.exit(1)

    print(f"正在从 {input_file} 读取数据中...")
    with open(input_file, 'rb+') as file:
        header = file.read(encrypt_size)  # 读取需要混淆的头部数据
        if noback:
            print(f"不需要创建头部备份！")
        else:
            print(f"正在创建头部的备份...")
            with open(backup_file, 'wb') as backup:
                backup.write(header)  # 备份头部数据

        print(f"正在混淆 {encrypt_size} 字节的数据...")
        obfuscated_header = bit_flip_bytes(header)
        file.seek(0)  # 重置文件指针到开始位置
        file.write(obfuscated_header)  # 直接写回原文件

    output_file = input_file + ".obf001"
    os.rename(input_file, output_file)
    print("混淆完成。如果操作失败，请使用备份文件恢复数据。")


def _deobfuscate_header(input_file: str, minimum_size: int = 1024*1024):

    if not input_file.endswith(".obf001"):
        print("错误: 文件后缀不正确，应以 '.obf001' 结尾")
        sys.exit(1)

    suffix = ".obf001"

    original_file = input_file[:-len(suffix)]  # 移除 ".obf001" 后缀
    encrypt_size = max(int(os.path.getsize(input_file) * 0.01), minimum_size)

    print(f"正在从 {input_file} 读取数据中...")
    with open(input_file, 'rb+') as file:
        obfuscated_header = file.read(encrypt_size)  # 读取混淆的头部数据
        # key = password.encode()
        print(f"正在解混淆 {len(obfuscated_header)} 字节的数据...")
        deobfuscated_header = bit_flip_bytes(obfuscated_header)
        file.seek(0)
        file.write(deobfuscated_header)  # 写回解混淆后的头部数据

    os.rename(input_file, original_file)
    print("解混淆完成。")
    print(f"正在尝试删除备份文件...")
    backup_file = original_file + ".headerbak"
    if not os.path.exists(backup_file):
        print(f"备份文件 {backup_file} 不存在，不需要删除！")
    else:
        print(f"正在删除备份文件 {backup_file}")
        os.remove(backup_file)


def default_cmd(input_file: str | None, deobfuscate: bool | None, noback: bool | None):
    input_file = input_file if input_file is not None else input("请输入文件名：")
    deobfuscate = deobfuscate if deobfuscate is not None else input_file.endswith(
        ".obf001")
    noback = noback if noback is not None else False

    if deobfuscate:
        _deobfuscate_header(input_file=input_file)
    else:
        _obfuscate_header(input_file=input_file, noback=noback)


def obfuscate_folder_cmd(deobfuscate: bool | None, noback: bool | None):
    deobfuscate = deobfuscate if deobfuscate is not None else False
    noback = noback if noback is not None else False

    for root, dirs, files in os.walk(global_targetpath):  # 遍历文件夹
        for filename in files:
            file_path = os.path.join(root, filename)
            if deobfuscate:
                if file_path.endswith(".obf001"):
                    try:
                        _deobfuscate_header(input_file=file_path)
                        # print(f"文件 {filename} 已解混淆。")
                    except Exception as e:
                        print(f"解混淆文件 {filename} 时发生错误：{e}")
            else:
                if file_path.endswith(".obf001"):
                    print(f"跳过已混淆文件 {filename}")
                    continue

                if file_path.endswith(".headerbak"):
                    print(f"跳过头部备份文件 {filename}")
                    continue

                try:
                    _obfuscate_header(input_file=file_path, noback=noback)
                    # print(f"文件 {filename} 已混淆。")
                except Exception as e:
                    print(f"混淆文件 {filename} 时发生错误：{e}")


def main(command=None, targetpath=None, all=None, deobfuscate=None, de=None, noback=None):
    global global_targetpath
    global_targetpath = targetpath or '.'
    if all is True:
        obfuscate_folder_cmd(deobfuscate=deobfuscate or de, noback=noback)
    else:
        default_cmd(input_file=command,
                    deobfuscate=deobfuscate or de)


if __name__ == "__main__":
    fire.Fire(main)
    # main()
