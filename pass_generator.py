from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    password = password[:72]  # tronquer pour éviter l'erreur bcrypt
    return pwd_context.hash(password)

password = "Tester-123"  # moins de 72 caractères, ok direct
hashed = hash_password(password)
print(hashed)