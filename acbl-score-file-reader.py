#!/usr/bin/env python
"""
ACBL Score Game File Parser
---------------------------
A Python 2.7 parser for ACBL Score game files based on the format described at:
https://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm
"""
import os
import struct
import datetime
from datetime import datetime, timedelta


class ACBLGameFileParser(object):
    """Parser for ACBL Score Game Files."""
    
    def __init__(self, filepath):
        """Initialize the parser with a file path.
        
        Args:
            filepath: Path to the ACBL Score game file
        """
        self.filepath = filepath
        self.file_data = None
        self.game_data = {}
        self.header = {}
        self.sections = []
        self.section_entries = {}
        
    def read_file(self):
        """Read the game file into memory.
        
        Returns:
            bool: True if file was read successfully, False otherwise
        """
        try:
            with open(self.filepath, 'rb') as f:
                self.file_data = f.read()
            return True
        except Exception as e:
            print("Error reading file: {0}".format(e))
            return False

    def parse_master (self) :
        event_types = [
            "Pairs", "Teams", "Individual", "Home Style pairs",
            "Board-A-Match Teams", "Series winner"
        ]
        
        pair_scoring_methods = {
            0: "Matchpoints", 1: "IMPs with computed datum",
            2: "Average IMPs", 3: "Total IMPs", 4: "Instant Matchpoints",
            5: "Board-a-Match Matchpoints", 13: "IMPs with predetermined datum",
            14: "Double Matchpoints (European)", 15: "Total Points"
        }
        
        team_scoring_methods = {
            6: "Win/Loss", 7: "Victory Points", 8: "Knockout",
            9: "ZIP Knockout", 16: "Board-a-Match Matchpoints",
            18: "Compact KO", 10: "Continuous Pairs (Series Winners)"
        }

        data = self.file_data 
        # Read Master Table header
        if len(data) < 0x0a14:
            raise ValueError("File too small to contain valid Master Table")

        # Unpack fixed position fields
        (table_length, ac3_id, file_length, first_free_block, 
         inst_match_table, event1_ptr, event2_ptr) = struct.unpack_from('<H3s4xLLL4xLL', data)

        # Validate AC3 identifier
        if ac3_id != b'AC3':
            raise ValueError("Invalid ACBLscore file identifier")

        # Read event types (50 bytes from 0x00da)
        event_types = list(struct.unpack_from('<50B', data, 0xda))

        # Read scoring methods (50 bytes from 0x010c)
        scoring_methods = list(struct.unpack_from('<50B', data, 0x10c))

        # Read version and timestamp (offset 0x09db)
        (version, creation_days, creation_minutes, 
         min_version, note_ptr, imp_table_ptr) = struct.unpack_from('<xxBBHxxLxxL', data, 0x9db)

        # Convert ACBLscore timestamp (days since 1899-12-30)
        creation_date = datetime(1899, 12, 30) + timedelta(days=creation_days)

        # Read global options (offset 0x09ec)
        global_options = struct.unpack_from('<B', data, 0x9ec)[0]

        # Read Bridgemate flag (offset 0x0a13)
        bridgemate_import = struct.unpack_from('<B', data, 0x0a13)[0]

        # Build result dictionary
        result = {
            'file_length': file_length,
            'events': [],
            'version': version / 100,
            'min_version': min_version / 100,
            'creation_date': creation_date,
            'bridgemate_import': bridgemate_import == 1,
            'global_options': {
                'backed_up': bool(global_options & 4)
            }
        }

        # Process events
        for i in range(50):
            if event_types[i] == 0 and event1_ptr == 0:
                break  # No more valid events
                
            event = {
                'type': event_types[event_types[i]] if event_types[i] < len(event_types) else "Unknown ({event_types[i]})",
                'scoring': pair_scoring_methods.get(scoring_methods[i], 
                       team_scoring_methods.get(scoring_methods[i], 
                       "Unknown ({scoring_methods[i]})"))
            }
            result['events'].append(event)

        return result
        

        
    def parse(self):
        """Parse the game file.
        
        Returns:
            dict: Parsed game data
        """
        if not self.file_data and not self.read_file():
            return {}
        
        self.parse_header()
        self.parse_sections()
        
        # Assemble the complete game data
        self.game_data = {
            'header': self.header,
            'sections': self.sections
        }
        
        return self.game_data
    
    def parse_header(self):
        """Parse the game file header information."""
        # Game file header is 148 bytes
        header_data = self.file_data[:148]
        
        # Extract header fields according to the spec
        self.header = {
            'club_number': self._decode_text(header_data[0:8]),
            'game_date': self._decode_date(header_data[8:12]),
            'game_session': ord(header_data[12]),
            'event_code': ord(header_data[13]),
            'director_name': self._decode_text(header_data[32:62]),
            'club_name': self._decode_text(header_data[62:94]),
            'game_type': ord(header_data[94]),
            'number_of_sections': ord(header_data[95]),
            'file_version': ord(header_data[96]),
        }
    
    def parse_sections(self):
        """Parse all sections in the game file."""
        # Start after the header
        pos = 148
        
        for section_idx in range(self.header['number_of_sections']):
            # Section record is 61 bytes
            section_data = self.file_data[pos:pos+61]
            pos += 61
            
            section = self._parse_section(section_data)
            self.sections.append(section)
            
            # Parse section entries
            entries = []
            num_entries = section['number_of_pairs']
            
            for _ in range(num_entries):
                # Each entry is 52 bytes
                entry_data = self.file_data[pos:pos+52]
                pos += 52
                
                entry = self._parse_section_entry(entry_data, section['section_letter'])
                entries.append(entry)
            
            # Store entries with section
            self.section_entries[section['section_letter']] = entries
            section['entries'] = entries
            
            # Skip to the next section if needed (alignment)
            if pos % 4 != 0:
                pos += 4 - (pos % 4)
    
    def _parse_section(self, section_data):
        """Parse a section record.
        
        Args:
            section_data: Bytes representing a section record
            
        Returns:
            dict: Parsed section data
        """
        return {
            'section_letter': chr(ord(section_data[0])),
            'movement': ord(section_data[1]),
            'number_of_tables': ord(section_data[2]),
            'number_of_boards': ord(section_data[3]),
            'number_of_pairs': ord(section_data[6]),
            'scoring_method': ord(section_data[9]),
            'average_score': ord(section_data[10]),
            'section_name': self._decode_text(section_data[21:41])
        }
    
    def _parse_section_entry(self, entry_data, section):
        """Parse a section entry record.
        
        Args:
            entry_data: Bytes representing a section entry
            section: Section letter
            
        Returns:
            dict: Parsed entry data
        """
        entry = {
            'section': section,
            'pair_number': struct.unpack('<H', entry_data[0:2])[0],
            'direction': 'NS' if ord(entry_data[2]) == 0 else 'EW',
            'player_numbers': [
                struct.unpack('<I', entry_data[6:10])[0],
                struct.unpack('<I', entry_data[10:14])[0]
            ],
            'player_names': [
                self._decode_text(entry_data[14:29]),
                self._decode_text(entry_data[29:44])
            ],
            'matchpoints': float(struct.unpack('<H', entry_data[44:46])[0]) / 100,
            'percentage': float(struct.unpack('<H', entry_data[46:48])[0]) / 100
        }
        
        # Calculate rank if available
        rank_data = entry_data[48:50]
        rank = struct.unpack('<H', rank_data)[0]
        if rank > 0:
            entry['rank'] = rank
        
        return entry
    
    def _decode_text(self, text_bytes):
        """Decode text bytes to string, handling null termination.
        
        Args:
            text_bytes: Bytes to decode
            
        Returns:
            str: Decoded text string
        """
        # Find null terminator if present
        try:
            null_pos = text_bytes.index('\0')
            text_bytes = text_bytes[:null_pos]
        except ValueError:
            pass
        
        # In Python 2.7, bytes are strings, so we can return directly after stripping
        return text_bytes.strip()

    def decode_date (self, loc) :
        """ Decode data string from the locatation in the file """
        dt = struct.unpack_from ('<L', self.file_data, loc)[0]
        date = dt >> 16
        year = (date >> 9) + 1980
        month = (date >> 5) & 0x0F
        day = (date & 0x1F)
        return (year, month, day) 

        
    def _decode_date(self, date_bytes):
        """Decode a 4-byte date representation.
        
        Args:
            date_bytes: 4 bytes representing a date
            
        Returns:
            str: Date in YYYY-MM-DD format
        """
        try:
            year = struct.unpack('<H', date_bytes[0:2])[0]
            month = ord(date_bytes[2])
            day = ord(date_bytes[3])
            
            # According to the spec, earliest date is 1/1/1970
            # If year is a small value, add 1900
            if year < 1970:
                year += 1900
                
            return "{0:04d}-{1:02d}-{2:02d}".format(year, month, day)
        except:
            return "Unknown date"
    
    def get_pair_results(self, section, pair_number):
        """Get detailed results for a specific pair.
        
        Args:
            section: Section letter
            pair_number: Pair number
            
        Returns:
            dict: Pair results
        """
        # This would need to parse the board results which follows the section entries
        # This implementation is incomplete as it requires parsing the board results
        # which can be added based on the specification
        return {}
    
    def display_summary(self):
        """Display a summary of the game file."""
        if not self.game_data:
            self.parse()
            
        print("ACBL Game File Summary")
        print("=====================")
        print("Club: {0} ({1})".format(self.header['club_name'], self.header['club_number']))
        print("Date: {0}".format(self.header['game_date']))
        print("Director: {0}".format(self.header['director_name']))
        print("Sections: {0}".format(self.header['number_of_sections']))
        
        for section in self.sections:
            print("\nSection {0}: {1}".format(section['section_letter'], section['section_name']))
            print("  Tables: {0}".format(section['number_of_tables']))
            print("  Boards: {0}".format(section['number_of_boards']))
            print("  Pairs: {0}".format(section['number_of_pairs']))
            
            # Top finishers (if entries were parsed)
            if section.get('entries'):
                # Sort by percentage
                top_finishers = sorted(
                    section['entries'], 
                    key=lambda x: x.get('percentage', 0), 
                    reverse=True
                )[:3]
                
                print("  Top Finishers:")
                for i, entry in enumerate(top_finishers):
                    players = " / ".join(entry['player_names'])
                    print("    {0}. {1} {2}: {3} - {4:.2f}%".format(
                        i+1, entry['pair_number'], entry['direction'], 
                        players, entry['percentage']))


def parse(file_path):
    """Main function to demonstrate usage."""
    import sys
    
    parser = ACBLGameFileParser(file_path)
    game_data = parser.parse()
    parser.display_summary()
    
    # Example of accessing the parsed data
    print("\nAccessing data programmatically:")
    if game_data and game_data.get('sections'):
        section = game_data['sections'][0]['section_letter']
        print("First section: {0}".format(section))
        
        if game_data['sections'][0].get('entries'):
            first_pair = game_data['sections'][0]['entries'][0]
            print("First pair: {0} {1}".format(first_pair['pair_number'], first_pair['direction']))
            print("  Players: {0} / {1}".format(first_pair['player_names'][0], first_pair['player_names'][1]))
            print("  Score: {0:.2f}%".format(first_pair['percentage']))

def main():
    """Main function to demonstrate usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python acbl_parser.py <game_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print("Error: File '{0}' not found.".format(file_path))
        sys.exit(1)
    
    parser = ACBLGameFileParser(file_path)
    game_data = parser.parse()
    parser.display_summary()
    
    # Example of accessing the parsed data
    print("\nAccessing data programmatically:")
    if game_data and game_data.get('sections'):
        section = game_data['sections'][0]['section_letter']
        print("First section: {0}".format(section))
        
        if game_data['sections'][0].get('entries'):
            first_pair = game_data['sections'][0]['entries'][0]
            print("First pair: {0} {1}".format(first_pair['pair_number'], first_pair['direction']))
            print("  Players: {0} / {1}".format(first_pair['player_names'][0], first_pair['player_names'][1]))
            print("  Score: {0:.2f}%".format(first_pair['percentage']))


parser = ACBLGameFileParser('250303.ACA')
parser.read_file()
data = parser.file_data


'''
parser.parse_header()

game_data = parser.parse()
parser.display_summary()
'''
