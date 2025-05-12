import os
import json
import google.generativeai as genai
import openai
from django.conf import settings
from PIL import Image
import cloudinary.uploader

class BirdIdentificationService:
    @staticmethod
    def enhance_image(image_file):
        """Enhance the image using Cloudinary's AI capabilities"""
        result = cloudinary.uploader.upload(
            image_file,
            transformation=[
                {'quality': 'auto:best'},
                {'effect': 'enhance'},
                {'effect': 'sharpen'}
            ]
        )
        return result['secure_url']

    @staticmethod
    def identify_bird_from_image(image_file, location_name=None):
        """Identify bird from image using Gemini Pro Vision"""
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # Prepare the image
        image = Image.open(image_file)
        
        # Create the prompt
        location_context = f" in {location_name}" if location_name else ""
        prompt = f"""
        Analyze this bird image{location_context} and provide the following information in JSON format:
        {{
            "identified_species": "Common name of the bird",
            "scientific_name": "Scientific name",
            "confidence_level": "Confidence percentage (0-100)",
            "key_features": ["List of identifying features"],
            "similar_species": ["List of similar species"],
            "habitat": "Typical habitat",
            "behavior": "Notable behavior observed",
            "additional_notes": "Any other relevant information"
        }}
        
        Please be as specific as possible with the identification and ensure the response is in valid JSON format.
        """
        
        try:
            response = model.generate_content([prompt, image])
            # Extract JSON from response
            json_str = response.text.strip('`').strip()
            if json_str.startswith('json'):
                json_str = json_str[4:]
            result = json.loads(json_str)
            
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def identify_bird_from_sound(sound_file, location_name=None):
        """Identify bird from sound using ChatGPT-4 and Whisper"""
        try:
            # First transcribe the audio using Whisper
            openai.api_key = settings.OPENAI_API_KEY
            
            audio_file = open(sound_file, "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            
            # Then analyze the sound pattern with GPT-4
            location_context = f" recorded in {location_name}" if location_name else ""
            prompt = f"""
            Analyze this bird sound transcription and pattern{location_context}:
            {transcript.text}
            
            Please provide the information in the following JSON format:
            {{
                "identified_species": "Common name of the bird",
                "scientific_name": "Scientific name",
                "confidence_level": "Confidence percentage (0-100)",
                "call_type": "Type of call (song, alarm, etc.)",
                "similar_species": ["List of species with similar calls"],
                "behavior": "Typical behavior associated with this call",
                "additional_notes": "Any other relevant information"
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert ornithologist specializing in bird call identification. Provide responses in JSON format only."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_bird_details_from_ai(bird_name):
        """Get detailed information about a bird using Gemini"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            Provide detailed information about the bird species "{bird_name}" in the following JSON format:
            {{
                "name": "Common name",
                "scientific_name": "Scientific name",
                "description": "Detailed description",
                "physical_characteristics": {{
                    "weight_range": "Weight range in grams",
                    "wingspan_range": "Wingspan in cm",
                    "length_range": "Length in cm"
                }},
                "classification": {{
                    "order": "Order name",
                    "family": "Family name"
                }},
                "habitat": "Detailed habitat information",
                "behavior": "Behavioral characteristics",
                "feeding_habits": "Feeding habits and diet",
                "breeding_info": "Breeding patterns and information",
                "migration_pattern": "Migration patterns if any",
                "conservation_status": "Current conservation status",
                "interesting_facts": ["Array of interesting facts"]
            }}
            
            Please ensure the response is in valid JSON format and all information is accurate.
            """
            
            response = model.generate_content(prompt)
            result = json.loads(response.text.strip('`').strip())
            
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 