import gzip
import sys
import base64

def gz_to_txt(input_path, output_path):
    print(output_path)
    with open(input_path, 'rb') as f_in: 
        binary_content = f_in.read()
        binary_string = base64.b64encode(binary_content).decode('utf-8')
        with open(output_path, 'w') as f_out:
            f_out.write(binary_string)

def txt_to_gz(input_path, output_path):
    with open(input_path, 'r') as f_in:
        binary_string = f_in.read()
        binary_content = base64.b64decode(binary_string)
        with open(output_path, 'wb') as f_out:
            f_out.write(binary_content)

def gz_to_hex(input_path, output_path):
    with open(input_path, 'rb') as f_in:
        binary_content = f_in.read()
        hex_string = binary_content.hex()
        with open(output_path, 'w') as f_out:
            f_out.write(hex_string)

def hex_to_gz(input_path, output_path):
    with open(input_path, 'r') as f_in:
        hex_string = f_in.read()
        binary_content = bytes.fromhex(hex_string)
        with open(output_path, 'wb') as f_out:
            f_out.write(binary_content)

def gz_to_bytes(input_path, output_path):
    with open(input_path, 'rb') as f_in:
        binary_content = f_in.read()
        with open(output_path, 'w') as f_out:
            f_out.write(str(binary_content))
        
def bytes_to_gz(input_path, output_path):
    with open(input_path, 'r') as f_in:
        binary_string = f_in.read()
        binary_content = eval(binary_string)
        with open(output_path, 'wb') as f_out:
            f_out.write(binary_content)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python utils.py <input_gz_file>")
        sys.exit(1)

    input_path = sys.argv[1]

    gz_to_txt(input_path, "b64_"+input_path)
    #txt_to_gz("b64_"+input_path, "output.cpc")
    #gz_to_hex(input_path, output_path)
    #hex_to_gz(output_path, "output.gz")
    #gz_to_bytes(input_path, output_path)
    #bytes_to_gz(output_path, "output.gz")
