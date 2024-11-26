import zipfile
import os
import gzip
import shutil


def compress_and_zip_folder(folder_path, zip_file_name):
    # Create a ZipFile object in write mode
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through all the files in the folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Create the full file path
                file_path = os.path.join(root, file)

                # Compress the file
                compressed_file_path = file_path + '.gz'
                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # Add the compressed file to the zip
                zipf.write(compressed_file_path, os.path.relpath(compressed_file_path, folder_path))

                # Optionally, delete the compressed file after adding to the zip
                os.remove(compressed_file_path)

    print(f"All files in '{folder_path}' have been compressed and zipped into '{zip_file_name}'.")

# Example usage
# folder_to_zip = r"C:/Users/Actowiz/Desktop/pagesave/snapdeal/25_11_2024"  # Replace with your folder path
folder_to_zip = r"C:/Users/Actowiz/Desktop/pagesave/sd_meesho_master/25_11_2024"  # Replace with your folder path
# zip_file_name = '//172.27.132.84/d/snapdeal_pagesave/25_11_2024.zip'  # Replace with your desired zip file name
zip_file_name = '//172.27.132.84/d/snapdeal_pagesave/25_11_2024_2.zip'  # Replace with your desired zip file name

compress_and_zip_folder(folder_to_zip, zip_file_name)
