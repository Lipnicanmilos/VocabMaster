import os
from dotenv import load_dotenv

def main():
    load_dotenv('env_config.txt')
    print("Current DATABASE_URL:", os.getenv("DATABASE_URL"))

if __name__ == "__main__":
    main()
