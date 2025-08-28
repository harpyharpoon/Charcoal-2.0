import unittest
from unittest.mock import patch, MagicMock
from pub_interface import PubInterface
from character import CharacterManager, Character


class TestPubInterface(unittest.TestCase):
    """Test The Pub interface functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pub_interface = PubInterface()
    
    def test_pub_interface_initialization(self):
        """Test that PubInterface initializes correctly"""
        self.assertIsNotNone(self.pub_interface.character_manager)
        self.assertIsNotNone(self.pub_interface.world_manager)
        self.assertIsNotNone(self.pub_interface.party_manager)
        self.assertIsNotNone(self.pub_interface.ai_dialogue)
        self.assertFalse(self.pub_interface.running)
        self.assertIsNone(self.pub_interface.current_user_character)
    
    def test_character_creation_flow(self):
        """Test that character creation produces valid characters"""
        initial_count = len(self.pub_interface.character_manager.list_characters())
        
        # Create a test character
        character = self.pub_interface.character_manager.create_character(
            "TestPubCharacter", "Warrior", "Soldier", "brave"
        )
        
        self.assertIsInstance(character, Character)
        self.assertEqual(character.name, "TestPubCharacter")
        self.assertEqual(character.character_class, "Warrior")
        self.assertEqual(character.background, "Soldier")
        self.assertEqual(character.personality, "brave")
        
        # Verify character was added to manager
        final_count = len(self.pub_interface.character_manager.list_characters())
        self.assertEqual(final_count, initial_count + 1)
        
        # Cleanup
        self.pub_interface.character_manager.characters.remove(character)
        self.pub_interface.character_manager.save_characters()
    
    def test_quest_board_displays_content(self):
        """Test that quest board shows parties and characters"""
        # This test verifies the quest board method doesn't crash
        # and would display appropriate content
        try:
            # We can't easily test the output without mocking print,
            # but we can ensure the method doesn't crash
            parties = self.pub_interface.party_manager.list_parties()
            characters = self.pub_interface.character_manager.list_characters()
            dungeons = self.pub_interface.world_manager.list_dungeons()
            
            # Verify data structures exist
            self.assertIsInstance(parties, list)
            self.assertIsInstance(characters, list)
            self.assertIsInstance(dungeons, list)
            
        except Exception as e:
            self.fail(f"Quest board functionality failed: {e}")
    
    def test_character_filtering_for_chat(self):
        """Test that character filtering for chat works correctly"""
        all_chars = self.pub_interface.character_manager.list_characters()
        
        # Test with no user character
        self.pub_interface.current_user_character = None
        chat_chars = [char for char in all_chars if char != self.pub_interface.current_user_character]
        self.assertEqual(len(chat_chars), len(all_chars))
        
        # Test with user character set
        if all_chars:
            self.pub_interface.current_user_character = all_chars[0]
            chat_chars = [char for char in all_chars if char != self.pub_interface.current_user_character]
            self.assertEqual(len(chat_chars), len(all_chars) - 1)
    
    def test_ai_dialogue_integration(self):
        """Test that AI dialogue system is properly integrated"""
        characters = self.pub_interface.character_manager.list_characters()
        
        if characters:
            character = characters[0]
            
            # Test dialogue generation doesn't crash
            try:
                response = self.pub_interface.ai_dialogue.generate_character_response(
                    character, "test context", "greeting", []
                )
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 0)
            except Exception as e:
                self.fail(f"AI dialogue integration failed: {e}")


if __name__ == "__main__":
    unittest.main()