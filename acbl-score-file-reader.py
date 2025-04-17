#!/usr/bin/env python
"""
ACBL Score Game File Parser
---------------------------
A Python parser for ACBL Score game files based on the format described at:
https://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm
"""

import os
import struct
import datetime
from datetime import datetime, timedelta
from acblscoresupportclasses import MasterTable, EventDetails, StratStructure, SectionSummary 
from acblscoresupportclasses import SectionDetails, SectionStrat, MitchellPair, PairDetails, PairList, MPAward
from acblscoresupportclasses import Ranking, Player, BoardEntry, BoardResults, BoardList

class ACBLGameFileParser(object):
    """Parser for ACBL Score Game Files."""
    event_max = 50
    section_max = 100
    max_mitchell = 40
    max_howell = 80 

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

    
    def __init__(self, filepath):
        """Initialize the parser with a file path.
        
        Args:
            filepath: Path to the ACBL Score game file
        """
        self.filepath = filepath
        self.file_data = None
        self.events = []
        self.event_type = []
        self.event_scoring = []
        self.sections = []

        self.game_data = {}
        self.header = {}
        self.sections = []
        self.section_entries = {}
        self.location = 0x0
        
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

    def parse_master_table (self) :
        data = self.file_data
        # Read Master Table header
        if len(data) < 0x0a14:
           raise ValueError("File too small to contain valid Master Table")


        cur_loc = 0

        (table_length, cur_loc) = self.decode_int16(cur_loc)
        if (table_length != 2578) :
            raise ValueError ("Table length incorrect (should be 2578): " + str(table_length))

        (ac3_id, cur_loc) = self.decode_string (cur_loc, 3)
        if ac3_id != b'AC3':
            raise ValueError("Invalid ACBLscore file identifier: " + ac3_id)

        (file_length, cur_loc) = self.decode_uint32 (cur_loc)
        if (file_length != len (data)) :
            raise ValueError ("File length and length of data read do not align: " +
                              str (file_length) + " / " +
                              str (len(data)))
        # don't care about free blocks for reading  
        (free_bloc, cur_loc) = self.decode_pointer(cur_loc)
        # this table is usually null so not following pointer right now 
        (instant_mp_table, cur_loc) = self.decode_pointer(cur_loc)

        for i in range (self.event_max) :
            (event_loc, cur_loc)  = self.decode_pointer (cur_loc)
            if event_loc :
                cur_event = self.parse_event_details(event_loc)
            else :
                cur_event = {}
            self.events.append ({'details': cur_event})

        for i in range (self.event_max) :
            (cur, cur_loc)  = self.decode_uint8 (cur_loc)
            self.events[i]['type'] = cur            

        for i in range (self.event_max) :
            (cur, cur_loc)  = self.decode_uint8 (cur_loc)
            self.events[i]['scoring'] = cur

        for i in range (self.section_max) :
            (cur, cur_loc)  = self.parse_section_summary(cur_loc)
            self.sections.append (cur)
        
        (memo_pointer, cur_loc) = self.decode_pointer(cur_loc)
        memo = self.parse_memo_structure (memo_pointer)
        (club_present, cur_loc) = self.decode_boolean(cur_loc)
        (score_version, cur_loc) = self.decode_intfloat2 (cur_loc)
        (create_date, cur_loc) = self.decode_date (cur_loc)
        (min_score_version, cur_loc) = self.decode_intfloat2 (cur_loc)
        (note_pointer, cur_loc) = self.decode_pointer(cur_loc)
        note = self.parse_note_structure (note_pointer)
        (ignored, cur_loc) = self.decode_string (cur_loc, 8)
        # predetermined imp tables are rarely used so not following for now
        (imp_table_ptr, cur_loc) = self.decode_pointer (cur_loc)
        (ignored, cur_loc) = self.decode_string (cur_loc, 7)
        (global_options, cur_loc) = self.decode_uint8 (cur_loc)
        (ignored, cur_loc) = self.decode_string (cur_loc, 21)
        (bridgemate, cur_loc) = self.decode_uint8 (cur_loc)
        
        self.header = MasterTable (score_version, memo, note,
                                   min_score_version, create_date, bridgemate,
                                   global_options) 

        return cur_loc
        
    def parse_event_details (self, cur_loc) :
        start = cur_loc
        
        (length, cur_loc) = self.decode_int16 (cur_loc)
        (num, cur_loc) = self.decode_int16 (cur_loc)
        (event_name, cur_loc) = self.decode_string (cur_loc, 25)
        (ses_name, cur_loc) = self.decode_string (cur_loc, 13)
        (director, cur_loc) = self.decode_string (cur_loc, 16)
        (sanction, cur_loc) = self.decode_string (cur_loc, 10)
        (date, cur_loc) = self.decode_string (cur_loc, 19)
        (club_name, cur_loc) = self.decode_string (cur_loc, 25)
        (event_code, cur_loc) = self.decode_string (cur_loc, 4)
        (ignore, cur_loc) = self.decode_string (cur_loc, 1)
        
        (mp_per, cur_loc) = self.decode_intfloat1 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 1)
        (per_qual, cur_loc) = self.decode_intfloat2 (cur_loc)
        (mp_rate, cur_loc) = self.decode_intfloat1 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 1)
        (age_strat, cur_loc) = self.decode_boolean (cur_loc)
        
        (rating, cur_loc) = self.decode_uint8 (cur_loc)
        (eoe, cur_loc) = self.decode_uint8 (cur_loc)
        (board_avg, cur_loc) = self.decode_uint16 (cur_loc)
        (ses_num, cur_loc) = self.decode_uint8 (cur_loc)
        (handicap, cur_loc) = self.decode_uint8 (cur_loc)
        (start_sess_num, cur_loc) = self.decode_uint8 (cur_loc)
        (carry_over, cur_loc) = self.decode_boolean (cur_loc)
        (data_ed, cur_loc) = self.decode_boolean (cur_loc)
        (neg_hand, cur_loc) = self.decode_boolean (cur_loc)
        (verified, cur_loc) = self.decode_uint8 (cur_loc)
        (ignored, cur_loc) = self.decode_uint8 (cur_loc)

        (max_imp_swing, cur_loc) = self.decode_uint8 (cur_loc)
        (club_ses, cur_loc) = self.decode_uint8 (cur_loc)
        (tie_break, cur_loc) = self.decode_intfloat2 (cur_loc)
        (perfect, cur_loc) = self.decode_uint16 (cur_loc)
        (top_on_board, cur_loc) = self.decode_uint16 (cur_loc)
        (ignore, cur_loc) = self.decode_uint16 (cur_loc)
        (num_strats, cur_loc) = self.decode_uint8 (cur_loc)
        (num_ses_total, cur_loc) = self.decode_uint8 (cur_loc)
        (consol_flag, cur_loc) = self.decode_boolean (cur_loc)
        (club_game, cur_loc) = self.decode_uint8 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc,6)
        (ignore, cur_loc) = self.decode_uint8 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc,3)
        (newcomers, cur_loc) = self.decode_uint16 (cur_loc)
        (club_number, cur_loc) = self.decode_string (cur_loc,6)

        (mod_time, cur_loc) = self.decode_date (cur_loc)
        (ignore, cur_loc) = self.decode_uint16 (cur_loc)
        
        (memo_ptr, cur_loc) = self.decode_pointer (cur_loc)
        memo = self.parse_memo_structure (memo_ptr)
        
        (ignore, cur_loc) = self.decode_uint8 (cur_loc)
        (num_brackets, cur_loc) = self.decode_uint8 (cur_loc)
        (bracket_number, cur_loc) = self.decode_uint8 (cur_loc)
        (ignore, cur_loc) = self.decode_uint8 (cur_loc)
        (qual_event_code, cur_loc) = self.decode_string (cur_loc, 4)
        (hand_award_meth, cur_loc) = self.decode_uint8 (cur_loc)
        (ignore, cur_loc) = self.decode_uint8 (cur_loc)
        (imp_calc_flag, cur_loc) = self.decode_boolean (cur_loc)
        (edxov, cur_loc) = self.decode_boolean (cur_loc)
        (contin_pairs, cur_loc) = self.decode_boolean (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc,2)
        (qualifying_event, cur_loc) = self.decode_boolean (cur_loc)
        (ignore, cur_loc) = self.decode_uint8 (cur_loc)

        (strat1_struct, cur_loc) = self.parse_strat_structure (cur_loc)
        (strat2_struct, cur_loc) = self.parse_strat_structure (cur_loc)
        (strat3_struct, cur_loc) = self.parse_strat_structure (cur_loc)
        (ignore, cur_loc) = self.decode_uint32 (cur_loc)
        (perc_qualify, cur_loc) = self.decode_uint8 (cur_loc)
        (ignore, cur_loc) = self.decode_uint8 (cur_loc)
        (lm_strat1, cur_loc) = self.decode_int8 (cur_loc)
        (lm_strat2, cur_loc) = self.decode_int8 (cur_loc)
        (lm_strat3, cur_loc) = self.decode_int8 (cur_loc)
        (nap_level, cur_loc) = self.decode_uint8 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc,65)

        (split_site_flag, cur_loc) = self.decode_boolean (cur_loc)
        (add_factor_multi, cur_loc) = self.decode_real48 (cur_loc)
        (acbl_hands, cur_loc) = self.decode_string (cur_loc, 8)
        (ignore, cur_loc) = self.decode_uint16 (cur_loc)
        (per_instead_of_mp, cur_loc) = self.decode_boolean (cur_loc)
        (ignore, cur_loc) = self.decode_boolean (cur_loc)
        (seniors, cur_loc) = self.decode_boolean (cur_loc)
        (restrictions, cur_loc) = self.decode_uint8 (cur_loc)
        (side_game, cur_loc) = self.decode_boolean (cur_loc)
        (mp_version, cur_loc) = self.decode_uint8(cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 21)
        
        (print_unpaid, cur_loc)= self.decode_boolean (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 8)
        (game_fee, cur_loc) = self.decode_real48(cur_loc)
        (table_fee, cur_loc) = self.decode_real48(cur_loc)
        (charity_fee, cur_loc) = self.decode_real48(cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 13)
        (charity_name, cur_loc) = self.decode_string (cur_loc, 50)
        (strat_avg, cur_loc) = self.decode_boolean (cur_loc)
        (recap_per, cur_loc) = self.decode_boolean (cur_loc)
        (nonacbl, cur_loc) = self.decode_boolean (cur_loc)
        
        results = EventDetails ( num, event_name, ses_name, director, sanction,
                  date, club_name, event_code, memo,
                  mp_per, per_qual, mp_rate, age_strat, rating,
                  eoe, handicap, ses_num, start_sess_num,carry_over,
                  data_ed, neg_hand, verified, max_imp_swing, club_ses,
                  tie_break, perfect, top_on_board, num_strats, num_ses_total,
                  consol_flag, club_game, newcomers, club_number, mod_time,
                  num_brackets, bracket_number, qual_event_code, hand_award_meth,
                  imp_calc_flag, edxov, contin_pairs, qualifying_event,
                  strat1_struct, strat2_struct, strat3_struct, perc_qualify,
                  lm_strat1, lm_strat2, lm_strat3, nap_level,
                  split_site_flag, add_factor_multi, acbl_hands,
                  per_instead_of_mp, seniors, restrictions, side_game,
                  mp_version, print_unpaid, game_fee, table_fee, charity_fee,
                  strat_avg, recap_per, nonacbl ) 
     
        return results

    def parse_strat_structure (self, cur_loc) :
        start = cur_loc 
        (ignore, cur_loc) = self.decode_string (cur_loc,15)
        (mp_first, cur_loc) = self.decode_intfloat2 (cur_loc)
        (color, cur_loc) = self.decode_uint8 (cur_loc)
        (depth, cur_loc) = self.decode_uint8 (cur_loc)
        (mp_factor, cur_loc) = self.decode_intfloat4 (cur_loc)
        (ignore, cur_loc) = self.decode_intfloat2 (cur_loc)
        (rank_depth, cur_loc) = self.decode_uint16 (cur_loc)
        (assumed_tables, cur_loc) = self.decode_uint16 (cur_loc)
        (omit, cur_loc) = self.decode_uint16 (cur_loc)
        (min_mps, cur_loc) = self.decode_uint16 (cur_loc)
        (mp_cutoff, cur_loc) = self.decode_uint16 (cur_loc)
        (strat_letter, cur_loc) = self.decode_char (cur_loc)

        (percent_of_open, cur_loc) = self.decode_uint8 (cur_loc)
        (event_m_factor, cur_loc) = self.decode_real48 (cur_loc)
        (ses_m_factor, cur_loc) = self.decode_real48 (cur_loc)
        (ignore, cur_loc) = self.decode_uint16 (cur_loc)

        (overall, cur_loc) = self.parse_mp_pigmentation_structure (cur_loc)
        (session, cur_loc) = self.parse_mp_pigmentation_structure (cur_loc)
        (section, cur_loc) = self.parse_mp_pigmentation_structure (cur_loc)

        result = StratStructure (mp_first, color, depth, mp_factor,rank_depth,
                  assumed_tables, omit, min_mps, mp_cutoff, strat_letter,
                  percent_of_open, event_m_factor, ses_m_factor,
                  overall,session, section )            
        return (result, cur_loc)

    def parse_mp_pigmentation_structure (self, cur_loc) :
        start = cur_loc
        (first_per, cur_loc) = self.decode_intfloat2 (cur_loc)
        (second_per, cur_loc) = self.decode_intfloat2 (cur_loc)
        (third_per, cur_loc) = self.decode_intfloat2 (cur_loc)
        (first_top, cur_loc) = self.decode_intfloat2 (cur_loc)
        (second_top, cur_loc) = self.decode_intfloat2 (cur_loc)
        (third_top, cur_loc) = self.decode_intfloat2 (cur_loc)
        (first_pig, cur_loc) = self.decode_uint8 (cur_loc)
        (second_pig, cur_loc) = self.decode_uint8 (cur_loc)
        (third_pig, cur_loc) = self.decode_uint8 (cur_loc)

        result = {
            'mp_percent_to_first_pig' : first_per,
            'mp_percent_to_second_pig' : second_per,
            'mp_percent_to_third_pig' : third_per,
            'mp_of_first_pig_to_top' : first_top,
            'mp_of_second_pig_to_top' : second_top,
            'mp_of_third_pig_to_top' : third_top,
            'first_pigmentation_type' : first_pig,
            'second_pigmentation_type' : second_pig,
            'third_pigmentation_type' : third_pig,
            }
        return (result, cur_loc) 
    
    def parse_section_summary (self, cur_loc) :
        start = cur_loc
        (num, cur_loc) = self.decode_uint8 (cur_loc)
        (name, cur_loc) = self.decode_string (cur_loc, 2)

        (details_ptr, cur_loc) = self.decode_pointer (cur_loc)
        details = self.parse_section_details (details_ptr)
        (boards_pt, cur_loc) = self.decode_pointer (cur_loc)
        boards = self.parse_boards_index (boards_pt) 
        
        
        (total_mps, cur_loc) = self.decode_uint16 (cur_loc)
        (status, cur_loc) = self.decode_uint8 (cur_loc)
        (prev_sec_score, cur_loc) = self.decode_uint8 (cur_loc)
        (next_sec_score, cur_loc) = self.decode_uint8 (cur_loc)
        (prev_sec_rank, cur_loc) = self.decode_uint8 (cur_loc)
        (next_sec_rank, cur_loc) = self.decode_uint8 (cur_loc)
        
        (num_rounds_entered, cur_loc) = self.decode_uint8 (cur_loc)
        (num_rounds_total, cur_loc) = self.decode_uint8 (cur_loc)
        (flags, cur_loc) = self.decode_uint8 (cur_loc)
        
        result = SectionSummary (num, name, details, boards,
                  total_mps, status, num_rounds_entered,
                  num_rounds_total, flags )
        return (result,cur_loc)

    def parse_section_details (self, cur_loc) :
        if (cur_loc == 0) :
            return (SectionDetails())
       
        start = cur_loc 
        (length, cur_loc) = self.decode_int16 (cur_loc)
        if (length != 802) :
            raise ValueError("Section details length not correct" ) 
        (sect_num, cur_loc) = self.decode_uint16 (cur_loc)

        
        (ns_pairs_pt, cur_loc) = self.decode_pointer (cur_loc)
        (ew_pairs_pt, cur_loc) = self.decode_pointer (cur_loc)
        (s_ind_pt, cur_loc) = self.decode_pointer (cur_loc)
        (w_ind_pt, cur_loc) = self.decode_pointer (cur_loc)

        ew_pairs = ''
        s_inds = ''
        w_inds = ''
        if (s_ind_pt ) : # pointers are for individuals NOT TESTED
            ns_pairs = self.parse_player_struct (ns_pairs_pt)
            ew_pairs = self.parse_player_struct (ew_pairs_pt)
            s_inds = self.parse_player_struct (s_ind_pt)
            w_inds = self.parse_player_struct (w_ind_pt)
        elif (ew_pairs_pt) : # pointer to pairs
            ns_pairs = self.parse_pair_index (ns_pairs_pt)
            ew_pairs = self.parse_pair_index (ew_pairs_pt)
        else :  # teams play  NOT TESTED 
            ns_pairs = self.parse_teams_index (ns_pairs_pt)

        
        (mp_pt, cur_loc) = self.decode_pointer (cur_loc)
        
        (howell_flag, cur_loc) = self.decode_boolean (cur_loc)
        (boards_in_play, cur_loc) = self.decode_uint16 (cur_loc)
        (highest_pair, cur_loc) = self.decode_uint16 (cur_loc)
        (boards_per_round, cur_loc) = self.decode_uint8 (cur_loc)
        (top_on_board, cur_loc) = self.decode_uint16 (cur_loc)
        (bye_stand_location, cur_loc) = self.decode_uint16 (cur_loc)
        (rover_movement, cur_loc) = self.decode_uint16 (cur_loc)
        (board_1_table, cur_loc) = self.decode_uint16 (cur_loc)
        (skip_round, cur_loc) = self.decode_uint16 (cur_loc)
        (ignore, cur_loc) = self.decode_uint16 (cur_loc)

        (names_entered, cur_loc) = self.decode_uint16 (cur_loc)
        (carry_over_flag, cur_loc) = self.decode_boolean (cur_loc)
        (max_number_played, cur_loc) = self.decode_uint8 (cur_loc)
        (board_factor, cur_loc) = self.decode_intfloat1 (cur_loc)
        (score_adjust, cur_loc) = self.decode_intfloat1 (cur_loc)
        (scores_factored_flag, cur_loc) = self.decode_boolean (cur_loc)
        (posting_method, cur_loc) = self.decode_uint8 (cur_loc)
        (posted, cur_loc) = self.decode_boolean (cur_loc)
        (num_rounds, cur_loc) = self.decode_uint16 (cur_loc)
        (movement_name, cur_loc) = self.decode_string (cur_loc,11)
        (phantom, cur_loc) = self.decode_int16 (cur_loc)
        (color_ind, cur_loc) = self.decode_uint8 (cur_loc)
        (dbadd_count, cur_loc) = self.decode_uint8 (cur_loc)
        (barometer_flag, cur_loc) = self.decode_boolean (cur_loc)
        (num_tables, cur_loc) = self.decode_uint16 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc,3)

        (total_mps, cur_loc) = self.decode_uint16 (cur_loc)
        (color_str, cur_loc) = self.decode_string (cur_loc,6)
        (ignore, cur_loc) = self.decode_string (cur_loc,3)
        (change_post_method, cur_loc) = self.decode_uint8 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc,3)
        (movement_flag, cur_loc) = self.decode_boolean (cur_loc)
        (max_board_play, cur_loc) = self.decode_uint8 (cur_loc)
        (outside_adj, cur_loc) = self.decode_boolean (cur_loc)
        (posting_sequence, cur_loc) = self.decode_uint8 (cur_loc)
        (rover_start, cur_loc) = self.decode_uint16 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc,1)

        (strat1, cur_loc) = self.parse_section_strat (cur_loc)
        (strat2, cur_loc) = self.parse_section_strat (cur_loc)
        (strat3, cur_loc) = self.parse_section_strat (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 1)

        (match_award, cur_loc) = self.decode_intfloat2 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 1)
        (vp_scale, cur_loc) = self.decode_uint8 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 2)
        (mod_time, cur_loc) = self.decode_date (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 15)
        
        (memo_ptr, cur_loc) = self.decode_pointer (cur_loc)
        memo = self.parse_memo_structure (memo_ptr)
        
        (bam_move, cur_loc) = self.decode_boolean (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 1)
        (score_version, cur_loc) = self.decode_intfloat2 (cur_loc)
        (phantom2, cur_loc) = self.decode_uint8 (cur_loc)
        (phantom3, cur_loc) = self.decode_uint8 (cur_loc)
        (manual_score_flag, cur_loc) = self.decode_boolean (cur_loc)

        if (howell_flag) :
            (pair_map, cur_loc) = self.parse_howell_pairs (cur_loc)
        else :
            (pair_map, cur_loc) = self.parse_mitchell_pairs (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 23)
        (club_num, cur_loc) = self.decode_string (cur_loc, 6)
        (ignore, cur_loc) = self.decode_uint8 (cur_loc)

        (match_index_ptr, cur_loc) = self.decode_pointer (cur_loc)
        team_match = self.parse_team_match_index (match_index_ptr)
        
        (strat1_pairs, cur_loc) = self.decode_uint16 (cur_loc)
        (strat2_pairs, cur_loc) = self.decode_uint16 (cur_loc)
        (strat3_pairs, cur_loc) = self.decode_uint16 (cur_loc)

        results = SectionDetails ()
        results.init_values (
            sect_num,
            ns_pairs, ew_pairs, s_inds, w_inds,
            howell_flag, boards_in_play, highest_pair,
            boards_per_round, top_on_board, bye_stand_location,
            rover_movement, board_1_table, skip_round,
            names_entered, carry_over_flag, max_number_played,
            board_factor, score_adjust, scores_factored_flag,
            posting_method, posted, num_rounds, movement_name,
            phantom, color_ind, dbadd_count, barometer_flag, num_tables,
            total_mps, color_str, change_post_method, movement_flag,
            max_board_play, outside_adj, posting_sequence,
            rover_start, strat1, strat2, strat3,
            match_award, vp_scale, mod_time, bam_move,
            score_version, phantom2, phantom3, manual_score_flag,
            pair_map, club_num, strat1_pairs, strat2_pairs, strat3_pairs,
            memo, team_match
            )
        return results

    def parse_section_strat (self, cur_loc) :
        start = cur_loc
        (ns_rank_depth, cur_loc) = self.decode_int16 (cur_loc)
        (ew_rank_depth, cur_loc) = self.decode_int16 (cur_loc)
        (s_rank_depth, cur_loc) = self.decode_int16 (cur_loc)
        (w_rank_depth, cur_loc) = self.decode_int16 (cur_loc)
        (ns_num, cur_loc) = self.decode_uint16 (cur_loc)
        (ew_num, cur_loc) = self.decode_uint16 (cur_loc)
        (s_num, cur_loc) = self.decode_uint16 (cur_loc)
        (w_num, cur_loc) = self.decode_uint16 (cur_loc)
        (ns_qual_depth, cur_loc) = self.decode_int16 (cur_loc)
        (ew_qual_depth, cur_loc) = self.decode_int16 (cur_loc)
        (s_qual_depth, cur_loc) = self.decode_int16 (cur_loc)
        (w_qual_depth, cur_loc) = self.decode_int16 (cur_loc)
        (ignore, cur_loc) = self.decode_uint8 (cur_loc)

        results = SectionStrat ()
        results.init_values (
            ns_rank_depth, ew_rank_depth, s_rank_depth, w_rank_depth,
            ns_num, ew_num, s_num, w_num,
            ns_qual_depth, ew_qual_depth, s_qual_depth, w_qual_depth
            )
            
        return (results, cur_loc)

    def parse_pair_index (self, cur_loc) :
        (length, cur_loc) = self.decode_int16 (cur_loc)
        (direction, cur_loc) = self.decode_uint16 (cur_loc)
        if (direction <1) or (direction >2) :
            raise ValueError ("invalid direction in pairs index table - must be 1 or 2 instead was " +
                              str (direction))
        (num_players, cur_loc) = self.decode_uint16 (cur_loc)
        if (num_players != 2) :
            raise ValueError ("Number of players must be 2, instead was " +
                              str (num_players))
        (num_pairs, cur_loc) = self.decode_uint16 (cur_loc)

        # not clear how to decode this data - pointers are outside of range
        (strat1_pt, cur_loc) = self.decode_pointer (cur_loc)
        (strat2_pt, cur_loc) = self.decode_pointer (cur_loc)
        (strat3_pt, cur_loc) = self.decode_pointer (cur_loc)
        
        pairs = [] 
        for i in range (num_pairs) :
            (ignore, cur_loc) = self.decode_string (cur_loc,3)
            (pair_struct_pt, cur_loc) = self.decode_pointer (cur_loc)
            pair_struct = self.parse_pair_struct (pair_struct_pt)
            pairs.append (pair_struct) 

        result = PairList (direction, num_pairs, pairs)
        return result

    def parse_pair_struct (self, cur_loc) :
        start = cur_loc 
        (length, cur_loc) = self.decode_int16 (cur_loc)
        (pair_id, cur_loc) = self.decode_uint16 (cur_loc)
        
        (adjustment, cur_loc) = self.decode_intfloat2long (cur_loc)
        (unscaled, cur_loc) = self.decode_intfloat2long (cur_loc)
        (ses_score, cur_loc) = self.decode_intfloat2long (cur_loc)
        (carry_over_score, cur_loc) = self.decode_intfloat2long (cur_loc)
        (final_score, cur_loc) = self.decode_intfloat2long (cur_loc)
        (handicap, cur_loc) = self.decode_intfloat2long (cur_loc)
        (partnership_per, cur_loc) = self.decode_intfloat2 (cur_loc)
        
        (partnership_strat, cur_loc) = self.decode_uint8 (cur_loc)
        (ignore, cur_loc) = self.decode_uint8 (cur_loc)
        (avg_mps, cur_loc) = self.decode_uint32 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 3)
        (next_session_sect, cur_loc) = self.decode_string (cur_loc, 2)
        (direction, cur_loc) = self.decode_char (cur_loc)
        (next_session_table, cur_loc) = self.decode_uint16 (cur_loc)
        (next_session_change, cur_loc) = self.decode_uint8 (cur_loc)
        (boards_played, cur_loc) = self.decode_uint16 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 1)
        (eligibility_status, cur_loc) = self.decode_uint8 (cur_loc)

        (prev_session_mp, cur_loc) = self.parse_mp_struct (cur_loc)
        (cur_session_mp, cur_loc) = self.parse_mp_struct (cur_loc)
        (all_session, cur_loc) = self.parse_mp_struct (cur_loc)

        (ignore, cur_loc) = self.decode_string (cur_loc, 5)
        
        (strat1_rank, cur_loc) = self.parse_ranking (cur_loc)
        (strat2_rank, cur_loc) = self.parse_ranking (cur_loc)
        (strat3_rank, cur_loc) = self.parse_ranking (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 9)

        (player1, cur_loc) = self.parse_player_struct (cur_loc)
        (player2, cur_loc) = self.parse_player_struct (cur_loc)
        
        result = PairDetails (
            pair_id, adjustment, unscaled, ses_score, carry_over_score,
            final_score, handicap, partnership_per, partnership_strat,
            avg_mps, next_session_sect, direction, next_session_table,
            next_session_change, boards_played, eligibility_status,
            prev_session_mp, cur_session_mp, all_session,
            strat1_rank, strat2_rank, strat3_rank, player1, player2)
        return result


    def parse_mp_struct (self, cur_loc) :
        (mp1, cur_loc) = self.decode_intfloat2 (cur_loc)
        (mp1_color, cur_loc) = self.decode_uint8 (cur_loc)
        (mp1_rank_type, cur_loc) = self.decode_uint8 (cur_loc)
        (mp2, cur_loc) = self.decode_intfloat2 (cur_loc)
        (mp2_color, cur_loc) = self.decode_uint8 (cur_loc)
        (mp2_rank_type, cur_loc) = self.decode_uint8 (cur_loc)
        (mp3, cur_loc) = self.decode_intfloat2 (cur_loc)
        (mp3_color, cur_loc) = self.decode_uint8 (cur_loc)
        (mp3_rank_type, cur_loc) = self.decode_uint8 (cur_loc)

        result = MPAward (
            mp1, mp1_color, mp1_rank_type,
            mp2, mp2_color, mp2_rank_type,
            mp3, mp3_color, mp3_rank_type
            )
        return (result, cur_loc)

    def parse_ranking (self, cur_loc) :
        (sect_rank, cur_loc) = self.decode_uint16 (cur_loc)
        (sect_tie, cur_loc) = self.decode_uint16 (cur_loc)
        (overall_rank, cur_loc) = self.decode_uint16 (cur_loc)
        (overall_tie, cur_loc) = self.decode_uint16 (cur_loc)
        (qual, cur_loc) = self.decode_uint16 (cur_loc)
        (rank, cur_loc) = self.decode_uint16 (cur_loc)
        (ind_next_lowest_rank_sec, cur_loc) = self.decode_uint16 (cur_loc)
        (sect_next_lowest_rank_sec, cur_loc) = self.decode_uint8 (cur_loc)
        (dir_next_lowest_rank_sec, cur_loc) = self.decode_uint8 (cur_loc)
        (ind_next_lowest_rank_overall, cur_loc) = self.decode_uint16 (cur_loc)
        (sect_next_lowest_rank_overall, cur_loc) = self.decode_uint8 (cur_loc)
        (dir_next_lowest_rank_overall, cur_loc) = self.decode_uint8 (cur_loc)

        result = Ranking (sect_rank, sect_tie, overall_rank, overall_tie,
                          qual, rank,
                          ind_next_lowest_rank_sec, sect_next_lowest_rank_sec, dir_next_lowest_rank_sec,
                          ind_next_lowest_rank_overall, sect_next_lowest_rank_overall, dir_next_lowest_rank_overall
                          )
        return (result, cur_loc)
        
    def parse_player_struct (self, cur_loc) :
        (last_name, cur_loc) = self.decode_string (cur_loc, 16)
        (first_name, cur_loc) = self.decode_string (cur_loc, 16)
        (city, cur_loc) = self.decode_string (cur_loc, 16)
        (state, cur_loc) = self.decode_string (cur_loc, 2)
        (acbl_num, cur_loc) = self.decode_string (cur_loc, 7)
        (db_key, cur_loc) = self.decode_string (cur_loc, 3)
        (wins, cur_loc) = self.decode_intfloat2 (cur_loc)
        (num_teams, cur_loc) = self.decode_intfloat2 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 1)
        (prev_session_mp, cur_loc) = self.parse_mp_struct (cur_loc)
        (cur_session_mp, cur_loc) = self.parse_mp_struct (cur_loc)
        (all_session, cur_loc) = self.parse_mp_struct (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 4)
        (total_mps, cur_loc) = self.decode_uint16 (cur_loc)
        (acbl_rank, cur_loc) = self.decode_char (cur_loc)
        (ignore, cur_loc) = self.decode_char (cur_loc)
        (country, cur_loc) = self.decode_string (cur_loc,2)

        result = Player (
            last_name, first_name,
            city, state, country,
            acbl_num, acbl_rank, total_mps,
            prev_session_mp, cur_session_mp, all_session)
        
        return (result, cur_loc) 

        
    def parse_mitchell_pairs (self, cur_loc) :
        start = cur_loc
        result = MitchellPair ()
        for i in range (self.max_mitchell) :
            (n, cur_loc) = self.decode_uint8 (cur_loc)
            (e, cur_loc) = self.decode_uint8 (cur_loc)
            (s, cur_loc) = self.decode_uint8 (cur_loc)
            (w, cur_loc) = self.decode_uint8 (cur_loc)
            result.add_reassignment ([n,e,s,w])

        for i in range (self.max_mitchell) :
            (n, cur_loc) = self.decode_uint8 (cur_loc)
            (e, cur_loc) = self.decode_uint8 (cur_loc)
            (s, cur_loc) = self.decode_uint8 (cur_loc)
            (w, cur_loc) = self.decode_uint8 (cur_loc)
            result.add_initial ([n,e,s,w])

        return (result, cur_loc)

    def parse_howell_pairs (self, cur_loc):
        result = HowellPair ()
        for i in range (self.max_howell) :
            (p, cur_loc) = self.decode_uint8 (cur_loc)
            result.add_reassignment (p)
        for i in range (self.max_howell) :
            (tn, cur_loc) = self.decode_uint8 (cur_loc)
            (d, cur_loc) = self.decode_uint8 (cur_loc)
            result.add_initial ([tn, d])
        (ignore, cur_loc) = self.decode_string (cur_loc, 79)
        raise ValueError ("Howell Movement parsing has not been verified - test then remove") 
        return (result, cur_loc) 

    def parse_team_match_index (self, cur_loc) :
        # not tested
        start = cur_loc
        if (cur_loc == 0) :
            return '' 
        (length, cur_loc) = self.decode_int16 (cur_loc)
        (sect_num, cur_loc) = self.decode_uint16 (cur_loc)
        (num_teams, cur_loc) = self.decode_uint16 (cur_loc)
        (num_rounds, cur_loc) = self.decode_uint16 (cur_loc)
        # follow pointer
        (table_assign, cur_loc) = self.decode_pointer (cur_loc)
        (cur_rount, cur_loc) = self.decode_uint8 (cur_loc)
        (num_posted, cur_loc) = self.decode_uint16 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc,1)
        (rr_1, cur_loc ) = self.parse_round_robin_struct (cur_loc)
        (rr_2, cur_loc ) = self.parse_round_robin_struct (cur_loc)
        # follow pointer
        (vp_pt, cur_loc) = self.decode_pointer (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc,24)
        team_matches = []
        for i in range (num_teams) :
            # follow pointer
            (team_match_pt, cur_loc) = self.decode_pointer (cur_loc)
            m = self.parse_team_match (teamp_match_pt)
            team_matches.append (m)
        result = MatchIndex (sect_num, num_teams, num_rounds,
                             table_assign, cur_round, num_posted,
                             rr_1, rr_2, team_matches)
        return result

    def parse_round_robin_struct (self, cur_loc) :
        (rr_active_flag, cur_loc) = self.decode_boolean (cur_loc)
        (rr_starting, cur_loc) = self.decode_int8 (cur_loc)
        (home_1_sect, cur_loc) = self.decode_string (cur_loc, 2)
        (direction_1, cur_loc) = self.decode_char (cur_loc)
        (table_1, cur_loc) = self.decode_int16 (cur_loc)
        (home_2_sect, cur_loc) = self.decode_string (cur_loc, 2)
        (direction_2, cur_loc) = self.decode_char (cur_loc)
        (table_2, cur_loc) = self.decode_int16 (cur_loc)
        (home_3_sect, cur_loc) = self.decode_string (cur_loc, 2)
        (direction_3, cur_loc) = self.decode_char (cur_loc)
        (table_3, cur_loc) = self.decode_int16 (cur_loc)
        
        result = RoundRobin (rr_active_flag, rr_starting,
                             home_1_sect, direction_1, table_1,
                             home_2_sect, direction_2, table_2,
                             home_3_sect, direction_3, table_3
                             )

        return (result, cur_loc) 

    def parse_team_match (self, cur_round) :
        (ignore, cur_loc) = self.decode_uint8 (cur_loc)
        (rnd, cur_loc) = self.decode_uint8 (cur_loc)
        (opp_team, cur_loc) = self.decode_uint16 (cur_loc)
        (num_rounds, cur_loc) = self.decode_uint8 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc, 1)
        (rr_status, cur_loc) = self.decode_uint8 (cur_loc)
        (imps, cur_loc) = self.decode_int16 (cur_loc)
        (vps, cur_loc) = self.decode_intfloat2 (cur_loc)
        (ignore, cur_loc) = self.decode_int8 (cur_loc)
        (boards_played, cur_loc) = self.decode_int8 (cur_loc)
        (ignore, cur_loc) = self.decode_int8 (cur_loc)
        (table, cur_loc) = self.decode_string (cur_loc, 2)
        (opp_2, cur_loc) = self.decode_int16 (cur_loc)
        (wins_on_round, cur_loc) = self.decode_intfloat2 (cur_loc)
        result = TeamMatch (rnd, opp_team, num_rounds, rr_status,
                            imps, vps, boards_played, table,
                            opp_2, wins_on_round)
        return result 


    def parse_boards_index (self, cur_loc) :
        start = cur_loc
        if (cur_loc == 0) :
            return '' 
        (length, cur_loc) = self.decode_int16 (cur_loc)
        (sect_num, cur_loc) = self.decode_uint16 (cur_loc)
        (num_boards, cur_loc) = self.decode_uint16 (cur_loc)
        (ignore, cur_loc) = self.decode_string (cur_loc,31)
        
        boards = []
        for i in range (num_boards) :
            (board_num, cur_loc) = self.decode_uint8 (cur_loc)
            (travellers, cur_loc) = self.decode_boolean (cur_loc)
            (num_results, cur_loc) = self.decode_uint16 (cur_loc)
            (res_pt, cur_loc) = self.decode_pointer (cur_loc)
            # eventually need to check for board 2 (pairs) or board 4 (individual) results
            # but that is for later
            board_results = self.parse_board2_results (res_pt)
            board_results.set_travellers (travellers)
            board_results.set_board_num (board_num)
            board_results.set_num_results (num_results)
            boards.append (board_results)
        result = BoardList (sect_num, num_boards, boards)
        return result

    def parse_board2_results (self, cur_loc) :
        start = cur_loc
        (length, cur_loc) = self.decode_int16 (cur_loc)
        (board_id, cur_loc) = self.decode_uint16 (cur_loc)
        (comp_units, cur_loc) = self.decode_uint8 (cur_loc)
        if (comp_units != 2) :
            raise ValueError ("Invalid value for board results table: " + str (comp_units))
        (num_results, cur_loc) = self.decode_uint8 (cur_loc)
        entries = []
        for i in range (num_results) :
            (rnd, cur_loc) = self.decode_uint8 (cur_loc)
            (table, cur_loc) = self.decode_uint8 (cur_loc)
            (ns, cur_loc) = self.decode_uint16 (cur_loc)
            (ns_score, cur_loc) = self.decode_uint16 (cur_loc)
            (ns_mp, cur_loc) = self.decode_intfloat2long (cur_loc)
            (ew, cur_loc) = self.decode_uint16 (cur_loc)
            (ew_score, cur_loc) = self.decode_uint16 (cur_loc)
            (ew_mp, cur_loc) = self.decode_intfloat2long (cur_loc)
            entry = BoardEntry (rnd, table,
                                ns, ns_score, ns_mp,
                                ew, ew_score, ew_mp)
            entries.append (entry)

        result = BoardResults (board_id, comp_units, num_results, entries)        
        return result
        
    def parse_memo_structure (self, cur_loc) :
        start = cur_loc
        if (cur_loc == 0) :
            return '' 
        (length, cur_loc) = self.decode_int16 (cur_loc)
        (memo_id, cur_loc) = self.decode_uint16 (cur_loc)
        (line_count, cur_loc) = self.decode_uint16 (cur_loc)
        lines = ''
        for i in range (line_count) :
            (line, cur_loc) = self.decode_string(63)
            lines = lines + ' ' + line
        return lines


    def parse_note_structure (self, cur_loc) :
        if (cur_loc == 0 ) :
            return '' 
        start = cur_loc
        (length, cur_loc) = self.decode_int16 (cur_loc)
        (note_id, cur_loc) = self.decode_uint16 (cur_loc)
        (line_count, cur_loc) = self.decode_uint16 (cur_loc)
        lines = ''
        for i in range (line_count) :
            (line, cur_loc) = self.decode_string(75)
            lines = lines + ' ' + line
        return lines
    

    def decode_date (self, loc) :
        """ Decode data string from the locatation in the file """
        dt = struct.unpack_from ('<L', self.file_data, loc)[0]
        date = dt >> 16
        year = (date >> 9) + 1980
        month = (date >> 5) & 0x0F
        day = (date & 0x1F)
        time = dt & 0xFFFF
        hour = time >> 11
        minute = (time >> 5) & 0x3F
        sec = (time << 1) & 0x3F
        res = datetime (year, month, day, hour, minute, sec)
        return (res, loc+4)

    def decode_string (self, loc, max_len) :
        length = struct.unpack_from("<B", self.file_data, loc)[0]
        val = struct.unpack_from ("<"+str(length)+"s", self.file_data, loc+1)[0]
        return (val, loc+max_len+1)

    def decode_char (self, loc) : 
        val = struct.unpack_from ('<c', self.file_data, loc)[0]
        return (val, loc+1)

    def decode_int8 (self, loc) : 
        val = struct.unpack_from ('<b', self.file_data, loc)[0]
        return (val, loc+1)

    def decode_uint8 (self, loc) : 
        val = struct.unpack_from ('<B', self.file_data, loc)[0]
        return (val, loc+1)

    def decode_int16 (self, loc) :
        val = struct.unpack_from ('<h', self.file_data, loc)[0]
        return (val, loc+2)

    def decode_uint16 (self, loc) :
        val = struct.unpack_from ('<H', self.file_data, loc)[0]
        return (val, loc+2)

    def decode_uint32 (self, loc) :
        val = struct.unpack_from ("<L", self.file_data, loc)[0]
        return (val, loc+4)
    
    def decode_intfloat1 (self, loc) :
        val = struct.unpack_from ("<h", self.file_data, loc)[0]
        val = val/10
        return (val, loc+2) 

    def decode_intfloat2 (self, loc) :
        val = struct.unpack_from ("<h", self.file_data, loc)[0]
        val = val/100
        return (val, loc+2) 


    def decode_intfloat2long (self, loc) :
        val = struct.unpack_from ("<l", self.file_data, loc)[0]
        val = val/100
        return (val, loc+4) 

    def decode_intfloat4 (self, loc) :
        val = struct.unpack_from ("<h", self.file_data, loc)[0]
        val = val/10000
        return (val, loc+2) 

    # decode a very odd number format from pascal real48 to something more modern
    # not entirely sure if the endian encoding is correct here, all of my test
    # data sets have a value of 0 for these data sets
    # might need to do something more like https://www.gamedev.net/forums/topic/326742-conversion-of-pascal-real48-48-bit-float-to-c-double/?page=2
    def decode_real48 (self, loc) :
        bytes_data = self.file_data[loc:loc+6]
        exponent = bytes_data[0]
        mantissa_bytes = bytes_data[1:6]
        sign_bit = (mantissa_bytes[0] & 0x80) >> 7
        mantissa_bytes = bytes([mantissa_bytes[0] & 0x7F]) + mantissa_bytes[1:]
        mantissa_int = int.from_bytes(mantissa_bytes)
        mantissa = mantissa_int / (1 << 39)
        if exponent == 0 and mantissa_int == 0:
            return (0.0, loc+6)
        result = mantissa * (2 ** (exponent - 129))
        if sign_bit:
            result = -result
        
        return (result, loc+6) 

    def decode_boolean (self, loc) : 
        val = struct.unpack_from ('<B', self.file_data, loc)[0]
        return (not(val == 0), loc+1)

    def decode_pointer (self, loc) :
        val = struct.unpack_from ("<L", self.file_data, loc)[0]
        return (val, loc+4)




 
parser = ACBLGameFileParser('../250303.ACA')
parser.read_file()
data = parser.file_data
parser.parse_master_table() 
sect = parser.sections[0].details


'''       
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
'''
'''       
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

'''
