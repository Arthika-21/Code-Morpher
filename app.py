from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend connection

# --- Configure Gemini API ---
genai.configure(api_key="AIzaSyBQUdwJFEfa22bP1XoghAR2CZERj9Rae9I")

model = genai.GenerativeModel("gemini-2.5-flash")

# --- Simple in-memory cache to store DSL -> Java results ---
dsl_cache = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_java():
    try:
        data = request.get_json()
        dsl_text = data.get("dsl_input", "")

        if not dsl_text:
            return jsonify({"error": "No DSL input provided"}), 400

        # ✅ Check if already cached
        if dsl_text in dsl_cache:
            return jsonify({"java_code": dsl_cache[dsl_text], "cached": True})

        # --- Prompt with DSL Rules ---
        prompt = f"""
        Convert the following DSL statement into Java code.

        DSL RULES:
        1. FILE STRUCTURE - Each Java response must begin with the full file structure: package, imports, class, and methods.
        2. CLASS DEFINITION - Every file must contain one public class. Use PascalCase class names.
        3. METHOD RULES - Methods must have full signature, including main() when required.
        4. VARIABLE NAMING - Use camelCase; constants in UPPER_SNAKE_CASE.
        5. IMPORT RULES - Include only necessary imports.
        6. INDENTATION & FORMATTING - Use 4 spaces per indent; braces required for all blocks.
        7. EXCEPTION HANDLING - Use try-catch with descriptive error messages only when the user requested.
        8. OUTPUT RULES - Use System.out.println() for output.
        9. COMMENT RULES -Use Only include comments if requested.
        10. CODE STYLE - Clean, consistent, no redundant code.
        11. LOGIC CLARITY - Must be complete and logically valid.
        12. DETERMINISTIC OUTPUT - If the same DSL is given again, produce the exact same code.

        DSL: {dsl_text}
        Please return only the valid Java code.
        """

        # --- Generate from Gemini ---
        response = model.generate_content(prompt)
        java_code = response.text.strip()

        # ✅ Cache the result
        dsl_cache[dsl_text] = java_code

        return jsonify({"java_code": java_code, "cached": False})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
