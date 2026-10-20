import hashlib
import base64
import json
import os

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

VEHICLE_FILE = "vehicles.json"


def sha256_hash():
    message = input("Enter text: ")
    print("SHA-256:", hashlib.sha256(message.encode()).hexdigest())


def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    with open("private_key.pem", "wb") as file:
        file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open("public_key.pem", "wb") as file:
        file.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print("Keys saved as private_key.pem and public_key.pem.")


def sign_message():
    if not os.path.exists("private_key.pem"):
        print("Generate a key pair first.")
        return

    with open("private_key.pem", "rb") as file:
        private_key = serialization.load_pem_private_key(file.read(), password=None)

    message = input("Enter message to sign: ")
    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("Signature (Base64):", base64.b64encode(signature).decode())


def verify_signature():
    if not os.path.exists("public_key.pem"):
        print("Generate a key pair first.")
        return

    message = input("Enter the original message: ")
    signature_text = input("Paste the Base64 signature: ")

    try:
        signature = base64.b64decode(signature_text, validate=True)
        with open("public_key.pem", "rb") as file:
            public_key = serialization.load_pem_public_key(file.read())

        public_key.verify(
            signature,
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Signature is valid.")
    except (InvalidSignature, ValueError, TypeError):
        print("Signature is invalid or the input is incorrect.")


def load_vehicles():
    if not os.path.exists(VEHICLE_FILE):
        return {}
    try:
        with open(VEHICLE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def register_vehicle():
    plate = input("Enter number plate: ").strip().upper()
    owner = input("Enter owner name: ").strip()
    model = input("Enter vehicle model: ").strip()

    if not plate or not owner or not model:
        print("All fields are required.")
        return

    vehicles = load_vehicles()
    if plate in vehicles:
        print("This number plate is already registered.")
        return

    vehicles[plate] = {"owner": owner, "model": model}
    with open(VEHICLE_FILE, "w", encoding="utf-8") as file:
        json.dump(vehicles, file, indent=4)
    print("Vehicle registered successfully.")


def find_vehicle():
    plate = input("Enter number plate to search: ").strip().upper()
    vehicle = load_vehicles().get(plate)

    if vehicle:
        print("Number plate:", plate)
        print("Owner:", vehicle["owner"])
        print("Model:", vehicle["model"])
    else:
        print("Vehicle not found.")


def main():
    while True:
        print("\n--- Cryptography and Blockchain Fundamentals ---")
        print("1. Generate SHA-256 hash")
        print("2. Generate public-private key pair")
        print("3. Sign a message")
        print("4. Verify a digital signature")
        print("5. Register a vehicle")
        print("6. Search vehicle by number plate")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            sha256_hash()
        elif choice == "2":
            generate_keys()
        elif choice == "3":
            sign_message()
        elif choice == "4":
            verify_signature()
        elif choice == "5":
            register_vehicle()
        elif choice == "6":
            find_vehicle()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select an option from the menu.")


if __name__ == "__main__":
    main()
