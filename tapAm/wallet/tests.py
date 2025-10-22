import base64

# Define your client ID and secret key
client_id = "IKIAFC1EB44661640CDEBE0E61E84083EDED1E3AFC72"
secret_key = "3C202BF6988A732133BA9B71891DB1C7C2D60622"

# Concatenate with a colon
concatenated_string = f"{client_id}:{secret_key}"

# Encode to Base64
encoded_bytes = base64.b64encode(concatenated_string.encode("utf-8"))
encoded_string = encoded_bytes.decode("utf-8")

# Output the Base64 encoded string
print("Base64 Encoded String:", encoded_string)

