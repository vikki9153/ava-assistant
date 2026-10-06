import os
import tempfile
import unittest

from voice_assistant import add_custom_command, build_welcome_page, handle_command, install_startup_shortcut


class VoiceAssistantTests(unittest.TestCase):
    def test_open_notepad(self):
        response = handle_command("open notepad")
        self.assertIn("notepad", response.lower())

    def test_time_command(self):
        response = handle_command("what time is it")
        self.assertIn("time", response.lower())

    def test_search_command(self):
        response = handle_command("search best python tutorials")
        self.assertIn("best python tutorials", response.lower())

    def test_hindi_greeting(self):
        response = handle_command("namaste")
        self.assertIn("namaste", response.lower())

    def test_hindi_time_command(self):
        response = handle_command("abhi samay kya hai")
        self.assertIn("samay", response.lower())

    def test_whatsapp_launch(self):
        response = handle_command("whatsapp kholo")
        self.assertIn("whatsapp", response.lower())

    def test_study_mode(self):
        response = handle_command("study mode")
        self.assertIn("study", response.lower())

    def test_wake_word_open_chrome(self):
        response = handle_command("hey assistant open chrome")
        self.assertIn("chrome", response.lower())

    def test_hindi_wake_word(self):
        response = handle_command("namaste assistant whatsapp kholo")
        self.assertIn("whatsapp", response.lower())

    def test_custom_personal_command(self):
        response = handle_command("open my project")
        self.assertIn("project", response.lower())

    def test_startup_shortcut_install(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = install_startup_shortcut(temp_dir)
            self.assertTrue(os.path.exists(result))

    def test_add_custom_command(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "custom_commands.json")
            result = add_custom_command("my notes", "notepad", config_path)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(config_path))

    def test_build_welcome_page(self):
        page = build_welcome_page()
        self.assertIn("Ava", page["title"]) 
        self.assertIn("assistant", page["subtitle"].lower())
        self.assertIn("premium", page["theme"].lower())


if __name__ == "__main__":
    unittest.main()
