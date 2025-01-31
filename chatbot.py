import os
import requests
import xmltodict
import llama_cpp

# 📌 Define Model Path
MODEL_FOLDER = "/Users/joshuabrooks/applehealth-4/models"
MODEL_FILE = "mistral-7b.Q4_K_M.gguf"  # Use Mistral 7B
MODEL_PATH = os.path.join(MODEL_FOLDER, MODEL_FILE)

# 📌 Check & Download Model if Missing
def download_model():
    if not os.path.exists(MODEL_FOLDER):
        os.makedirs(MODEL_FOLDER)

    if not os.path.exists(MODEL_PATH):
        print("🚀 Downloading Mistral 7B model... (This may take a while)")

        url = "https://huggingface.co/TheBloke/Mistral-7B-GGUF/resolve/main/mistral-7b.Q4_K_M.gguf"
        response = requests.get(url, stream=True)

        with open(MODEL_PATH, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)

        print("✅ Model downloaded successfully!")

# 📌 Extract & Parse Full Health Data from XML
def extract_health_data(xml_file):
    with open(xml_file, "r", encoding="utf-8") as file:
        xml_data = file.read()
        parsed_data = xmltodict.parse(xml_data)

    structured_data = "Health Data Summary:\n"

    if "HealthData" in parsed_data:
        # Extract Records
        for record in parsed_data["HealthData"].get("Record", []):
            type_ = record["@type"]
            value = record.get("@value", "Unknown")
            unit = record.get("@unit", "")
            timestamp = record.get("@creationDate", "No Date")
            structured_data += f"{timestamp} | {type_}: {value} {unit}\n"

        # Extract Clinical Records (Diseases, Allergies, etc.)
        for condition in parsed_data["HealthData"].get("ClinicalRecord", []):
            structured_data += f"Condition: {condition.get('@displayName', 'Unknown')}\n"

        # Extract Workouts
        for workout in parsed_data["HealthData"].get("Workout", []):
            structured_data += f"Workout: {workout.get('@workoutActivityType', 'Unknown')} - {workout.get('@duration', 'Unknown')} min\n"

    return structured_data

# 📌 Ensure Model is Available
download_model()

# 📌 Load Mistral 7B Model
print("🚀 Loading Mistral 7B Model...")
llm = llama_cpp.Llama(model_path=MODEL_PATH)
print("✅ Model Loaded Successfully!")

# 📌 Chatbot Function
def chat_with_mistral():
    xml_file = "export.xml"  # Update with actual XML file
    health_data = extract_health_data(xml_file)

    print("✅ Health Data Loaded! You can now ask questions about your health.")
    
    while True:
        user_query = input("\nYou: ")
        if user_query.lower() in ["exit", "quit"]:
            print("Exiting chatbot...")
            break

        prompt = f"My health records:\n{health_data}\n\nUser Query: {user_query}"
        response = llm(prompt, max_tokens=300)

        print("\nAI:", response["choices"][0]["text"].strip())

if __name__ == "__main__":
    chat_with_mistral()
