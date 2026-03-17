import yaml
import requests

def main():
    print("Doing something with yaml and requests")
    data = yaml.safe_load("foo: bar")
    resp = requests.get("https://example.com")
    print(resp.status_code)

if __name__ == "__main__":
    main()
