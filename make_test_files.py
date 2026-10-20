import zipfile, tarfile, os
os.makedirs("temp_test_source/data", exist_ok=True)
with open("temp_test_source/data/target1.json", "w") as f: f.write('{"status": "root"}')
with open("temp_test_source/data/target2.json", "w") as f: f.write('{"status": "deep"}')
with open("temp_test_source/ignore_me.txt", "w") as f: f.write("ignore")
with zipfile.ZipFile("temp_test_source/inner_archive.zip", "w") as z: z.write("temp_test_source/data/target2.json", "data/target2.json")
with zipfile.ZipFile("nested_sample.zip", "w") as z:
    z.write("temp_test_source/data/target1.json", "target1.json")
    z.write("temp_test_source/ignore_me.txt", "ignore_me.txt")
    z.write("temp_test_source/inner_archive.zip", "nested_folder/inner_archive.zip")
print("SUCCESS: created nested_sample.zip")
