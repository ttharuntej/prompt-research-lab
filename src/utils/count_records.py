import json

def count_records():
    try:
        with open('eval_data.json', 'r') as f:
            data = json.load(f)
            count = len(data.get('rows', []))
            print(f"\nTotal records in eval_data.json: {count}")
            return count
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return 0

if __name__ == "__main__":
    count_records() 