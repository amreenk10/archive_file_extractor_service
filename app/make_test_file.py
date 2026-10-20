import zipfile
import tarfile
import os


os.makedirs("temp_test_source/data", exist_ok=True)

with open("temp_test_source/data/target1.json","w") as f:
    f.write('{"name": "root_file", "description": "I am in the base archive layer"}')

with open("temp_test_source/data/target2.json","w") as f:
    f.write('{"name": "deep_file","description":"I am hidden inside nested layers"}')

with open("temp_test_source/ignore_me.txt", "w") as f:
    f.write("This file should be skipped by the json glob filter")

print("Generating inner compressed files...")

with zipfile.ZipFile("temp_test_source/inner_archive.zip", "w") as z:
    z.write("temp_test_source/data/target2.json", "data/target2.json")

with tarfile.open("temp_test_source/deep_nested.tar.gz", "w:gz") as tar:
    tar.add("temp_test_source/data/target2.json", "data/target2.json")

with zipfile.ZipFile("nested_sample.zip", "w") as z:
    z.write("temp_test_source/data/target1.json", "target1.json")
    z.write("temp_test_source/ignore_me.txt", "ignore_me.txt")
    z.write("temp_test_source/inner_archive.zip", "nested_folder/inner_archive.zip")
    z.write("temp_test_source/deep_nested.tar.gz", "deep_folder/deep_nested.tar.gz")

with tarfile.open("nested_sample.tar.gz", "w:gz") as tar:
    tar.add("temp_test_source/data/target1.json", "target1.json")
    tar.add("temp_test_source/ignore_me.txt", "ignore_me.txt")
    tar.add("temp_test_source/inner_archive.zip", "nested_folder/inner_archive.zip")
    tar.add("temp_test_source/deep_nested.tar.gz", "deep_folder/deep_nested.tar.gz")

print("--- SUCCESS ---")
print("Generated 'nested_sample.zip' and 'nested_sample.tar.gz' in your directory!")
