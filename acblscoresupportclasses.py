
''' Classes to support ACBL Score Scripts
    based on the format described at:
        https://lajollabridge.com/Articles/ACBLscoreGameFilesDecoded.htm
'''

class MasterTable (object) :
    def __init__ (self,
                  score_version, memo, note,
                  min_score_version, create_date, bridgemate,
                  global_options) :
        self.version = score_version
        self.memo = memo
        self.note = note
        self.min_version = min_score_version
        self.creation_date = create_date
        self.bridgemate_import: bridgemate
        global_options = global_options


class EventDetails (object) :
    def __init__ (self,
                 num, event_name, ses_name, director, sanction,
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
                  strat_avg, recap_per, nonacbl ) :
        self.num = num
        self.event_name = event_name
        self.session_name = ses_name
        self.director = director
        self.tournament_sanction = sanction
        self.date = date
        self.club_name =  club_name
        self.event_code = event_code
        self.memo = memo
        self.mp_percentage_p_factor = mp_per
        self.percent_qualifying = per_qual
        self.mp_rating_t_factor = mp_rate
        self.stratify_by_age = age_strat
        self.rating = rating
        self.end_of_event_flag = eoe
        self.handicap = handicap
        self.session_number = ses_num
        self.starting_session_number = start_sess_num
        self.carryover_calculated = carry_over
        self.data_edited = data_ed
        self.negative_handicap_flag = neg_hand
        self.mp_award_verified = verified
        self.max_imp_swing = max_imp_swing
        self.club_session = club_ses
        self.tie_break_spread = tie_break
        self.mps_for_perfect_game = perfect
        self.top_on_a_board = top_on_board
        self.number_strats = num_strats
        self.total_number_sessions = num_ses_total
        self.consolation_flag = consol_flag
        self.club_game_type = club_game
        self.number_newcomer_tables = newcomers
        self.club_number = club_number
        self.event_modification_time = mod_time
        self.number_brackets = num_brackets
        self.backet_number = bracket_number
        self.qualifying_event_code = qual_event_code
        self.handicap_dual_ranking_method = hand_award_meth
        self.imp_datum_calc_flag = imp_calc_flag
        self.edxov_done = edxov
        self.continious_pairs_flag = contin_pairs
        self.qualifying_event_flag = qualifying_event
        self.strat1_structure = strat1_struct
        self.strat2_structure = strat2_struct
        self.strat3_structure = strat3_struct
        self.percent_to_qualify = perc_qualify
        self.lm_eligibility_strat_1 = lm_strat1
        self.lm_eligibility_strat_2 = lm_strat2
        self.lm_eligibility_strat_3 = lm_strat3
        self.level_for_nap_or_gnt =  nap_level
        self.split_site_flag =  split_site_flag
        self.additional_factor_for_multi_site_events = add_factor_multi
        self.set_number_of_ACBL_hands = acbl_hands
        self.display_percentages_instead_of_mps = per_instead_of_mp
        self.senior_event = seniors
        self.event_restrictions = restrictions
        self.side_game_flag = side_game
        self.version_of_mp_award = mp_version
        self.print_unpaid_flag = print_unpaid
        self.game_sanction_fee = game_fee
        self.table_sanction_fee = table_fee
        self.charity_sanction_fee = charity_fee
        self.stratify_by_average_flag = strat_avg
        self.recaps_in_percent_flag = recap_per
        self.non_acbl_flag = nonacbl


class StratStructure (object):
    def __init__ (self,
                  mp_first, color, depth, mp_factor,rank_depth,
                  assumed_tables, omit, min_mps, mp_cutoff, strat_letter,
                  percent_of_open, event_m_factor, ses_m_factor,
                  overall,session, section ):
        self.mps_for_first = mp_first
        self.ribbon_qualifying_color = color
        self.ribbon_qualifying_depth = depth
        self.mp_factor = mp_factor
        self.rank_depth = rank_depth
        self.number_tables_assumed = assumed_tables
        self.rank_to_omit = omit
        self.strat_min_mps = min_mps
        self.strat_mp_cutoff = mp_cutoff
        self.strat_letter = strat_letter
        self.percent_of_open_game_rating = percent_of_open
        self.event_m_factor = event_m_factor
        self.session_m_factor = ses_m_factor
        self.overall_award = overall
        self.session_award = session
        self.section_award = section


class SectionSummary (object) :
    def __init__ (self,
                  num, name, details, boards,
                  total_mps, status, num_rounds_entered,
                  num_rounds_total, flags ) :
        self.section_number = num
        self.section_name = name
        self.details = details
        self.boards = boards
        self.total_mp_score = total_mps
        self.scoring_status = status
        self.num_rounds_posted = num_rounds_entered
        self.total_number_rounds = num_rounds_total
        self.flags = flags
    
class SectionDetails (object) :

    def __init__ (self) :
        self.details = {}

            
    def init_values (
        self, sect_num, ns_pairs, ew_pairs, s_ind, w_ind,
        howell_flag, boards_in_play, highest_pair,
        boards_per_round, top_on_board, bye_stand,
        rover_movement, board_1_table, skip_round,
        names_entered, carry_over_flag, max_number_played,
        board_factor, score_adjust, scores_factored_flag,
        posting_method, posted, num_rounds, movement_name,
        phantom, color_ind, dbadd_count, barometer_flag, num_tables,
        total_mps, color_str, change_post_method, movement_flag,
        max_board_play, outside_adj, posting_sequence,
        rover_start, strat1, strat2, strat3, 
        match_award, vp_scale, mod_time, bam_move,
        score_version, phantom2, phantom3, manual_score,
        pair_map, club_num, strat1_pairs, strat2_pairs, strat3_pairs,
        memo, team_match
        ) :
        
        self.section_number = sect_num
        self.ns_pairs = ns_pairs
        self.ew_pairs = ew_pairs
        self.south_ind = s_ind
        self.west_ind = w_ind
        self.howell_flag = howell_flag
        self.num_boards_in_play = boards_in_play
        self.highest_pair_numbe = highest_pair
        self.num_boards_per_round = boards_per_round
        self.top_on_board = top_on_board
        self.location_of_bye_stand = bye_stand
        self.rover_movement_mode = rover_movement
        self.starting_table_for_board_1 = board_1_table
        self.ew_skip_after_round = skip_round
        self.names_entered_status = names_entered
        self.carry_over_scores_flag = carry_over_flag
        self.max_number_boards_to_play = max_number_played
        self.board_factor = board_factor
        self.score_adjust_average = score_adjust
        self.scores_factored_flag = scores_factored_flag
        self.posting_method = posting_method
        self.posted_flag = posted
        self.num_rounds = num_rounds
        self.movement_name = movement_name
        self.phantom_pair_number = phantom
        self.section_color_ind = color_ind
        self.dbadd_count = dbadd_count
        self.barometer_game_flag = barometer_flag
        self.num_tables = num_tables
        self.total_mp_score = total_mps
        self.section_color_str = color_str
        self.round_for_change_in_posting_method = change_post_method
        self.web_movement_flag = movement_flag
        self.max_times_board_played = max_board_play
        self.outside_adjustments_entered_flag = outside_adj
        self.sequence_used_in_posting = posting_sequence
        self.table_for_rover_pair_start = rover_start
        self.strat1 = strat1
        self.strat2 = strat2
        self.strat3 = strat3,
        self.match_award_mps = match_award
        self.victory_point_scale = vp_scale
        self.section_modification_time = mod_time
        self.bam_movement_flag = bam_move
        self.acbl_score_version = score_version
        self.phantom_player_2 = phantom2
        self.phantom_player_3 = phantom3
        self.manual_scoring_flag = manual_score
        self.pair_map = pair_map
        self.club_number = club_num
        self.num_elibible_strat1_pairs = strat1_pairs
        self.num_elibible_strat2_pairs = strat2_pairs
        self.num_elibible_strat3_pairs = strat3_pairs
        self.memo =  memo
        self.team_match = team_match


class SectionStrat (object) :
    def __init__ (self) :
        strat = {}

    def init_values (self,
                     ns_rank_depth, ew_rank_depth,
                     s_rank_depth, w_rank_depth,
                     ns_num, ew_num, s_num, w_num,
                     ns_qual_depth, ew_qual_depth,
                     s_qual_depth, w_qual_depth
                     ) :
        self.strat = {
            "ns_rank_depth" : ns_rank_depth,
            'ew_rank_depth' : ew_rank_depth,
            's_rank_depth' : s_rank_depth,
            'w_rank_depth' : w_rank_depth,
            'num_ns_pairs' : ns_num,
            'num_ew_pairs' : ew_num,
            'num_s_players' : s_num,
            'num_w_players' : w_num,
            'ns_qualification_depth' : ns_qual_depth,
            'ew_qualification_depth' : ew_qual_depth,
            's_qualification_depth' : s_qual_depth,
            'w_qualification_depth' : w_qual_depth
        }

class PairList (object) :
    def __init__ (self, direction, num_pairs, pairs):
        self.direction = direction
        self.num_pairs = num_pairs;
        self.pairs = pairs

class PairDetails (object) :
    def __init__ (self,
            pair_id, adjustment, unscaled, ses_score, carry_over_score,
            final_score, handicap, partnership_per, partnership_strat,
            avg_mps, next_session_sect, direction, next_session_table,
            next_session_change, boards_played, eligibility_status,
            prev_session_mp, cur_session_mp, all_session_mp,
            strat1_rank, strat2_rank, strat3_rank, player1, player2) :

        self.pair_id = pair_id
        self.adjustment = adjustment
        self.unscaled_score = unscaled
        self.session_score = ses_score
        self.carry_over_score = carry_over_score
        self_final_score = final_score
        self.handicap = handicap
        self.partnership_percentage = partnership_per
        self.partnership_strat = partnership_strat
        self.partnership_avg_mps = avg_mps
        self.next_sect = next_session_sect
        self.next_direction = direction
        self.next_table = next_session_table
        self.next_rotate = next_session_change
        self.num_boards_played = boards_played
        self.eligibility_status = eligibility_status
        self.prev_session_mps = prev_session_mp
        self.cur_sessoin_mps = cur_session_mp
        self.all_session_mps = all_session_mp
        self.strat1_rank = strat1_rank
        self.strat2_rank = strat2_rank
        self.strat3_rank = strat3_rank
        self.player1 = player1
        self.player2 = player2

    def print(self) :
        print (self.player1.print_string() + ' & ' +
               self.player2.print_string())
        

class MPAward (object):
    def __init__ (self,
                  mp1, mp1_color, mp1_rank_type,
                  mp2, mp2_color, mp2_rank_type,
                  mp3, mp3_color, mp3_rank_type
                  ) :
        self.mp1 = mp1
        self.mp1_color = mp1_color
        self.mp1_rank_type = mp1_rank_type
        self.mp2 = mp2
        self.mp2_color = mp2_color
        self.mp2_rank_type = mp2_rank_type
        self.mp3 = mp3
        self.mp3_color = mp3_color
        self.mp3_rank_type = mp3_rank_type

class Ranking (object) :
    
    def __init__ (self,
                  sect_rank, sect_tie, overall_rank, overall_tie,
                  qual, rank,
                  ind_next_lowest_rank_sec, sec_next_lowest_rank_sec, dir_next_lowest_rank_sec,
                  ind_next_lowest_rank_overall, sec_next_lowest_rank_overall, dir_next_lowest_rank_overall
                  ) :
        self.section_rank_with_mps = sect_rank
        self.sect_rank_tie = sect_tie
        self.overall_rank_with_mps = overall_rank
        self.overall_rank_with_tie = overall_tie
        self.qualification_flag = qual
        self.overall_rank = rank
        self.index_next_sect = ind_next_lowest_rank_sec
        self.section_next_sect = sec_next_lowest_rank_sec
        self.direction_next_ext = dir_next_lowest_rank_sec
        self.index_next_overall = ind_next_lowest_rank_overall
        self.section_next_oeverall = sec_next_lowest_rank_overall
        self.direction_next_overall = dir_next_lowest_rank_overall

class Player (object) :
    def __init__ (self,
                  last_name, first_name,
                  city, state, country,
                  acbl_num, acbl_rank, total_mps,
                  prev_session_mp, cur_session_mp, all_session
                  ) :
        self.last_name = last_name.decode()
        self.first_name = first_name.decode()
        self.city = city.decode()
        self.state = state.decode()
        self.country = country.decode()
        self.acbl_num = acbl_num.decode()
        self.acbl_rank = acbl_rank.decode()
        self.total_mps = total_mps
        self.mps_from_prev_session = prev_session_mp
        self.mps_from_current_session = cur_session_mp
        self.mps_total = all_session

    def print_string (self) :
        return (self.first_name + ' ' + self.last_name +
               ' ' + self.acbl_num + ' (' + self.acbl_rank + ')')
    def print (self) :
        print (self.print_string())
                  

class RoundRobin (object) :
    def __init__ (self,
                  rr_active_flag, rr_starting,
                  home_1_sect, direction_1, table_1,
                  home_2_sect, direction_2, table_2,
                  home_3_sect, direction_3, table_3
                  ) :
        self.active_flag = rr_active_flag
        self.starting_round = rr_starting
        self.team_1_home_table_section = home_1_sect
        self.team_1_direction = direction_1
        self.team_1_table_num = table_1
        self.team_2_home_table_section = home_2_sect
        self.team_2_direction = direction_2
        self.team_2_table_num = table_2
        self.team_3_home_table_section = home_3_sect
        self.team_3_direction = direction_3
        self.team_3_table_num = table_3


class MatchIndex (object):
    def __init__ (self,
                  sect_num, num_teams, num_rounds,
                  table_assign, cur_round, num_posted,
                  rr_1, rr_2, team_matches
                  ) :
        self.section_num = sect_num
        self.num_teams = num_teams
        self.num_rounds = num_rounds
        self.table_assignments = table_assign
        self.current_round = cur_round
        self.num_teams_posted = num_posted
        self,round_robin_1 = rr_1
        self.rounc_robin_2 = rr_2
        self.team_matches = team_matches

class TeamMatch (object) :
    def __init__ (self,
                  rnd, opp_team, num_rounds, rr_status,
                  imps, vps, boards_played, table,
                  opp_2, wins_on_round) :
        self.round_num = rnd
        self.opponent_team_num = opp_team
        self.num_rounds = num_rounds
        self.round_robin_status = rr_status
        self.imps = imps
        self.victory_points = vps
        self.boards_played = boards_played
        self.table_letter = table
        self.second_opponent = opp_2
        self.wins_on_round = wins_on_round

       
class BoardList (object) :
    def __init__ (self,
                  sect_num, num_boards, boards) :
        self.section_num = sect_num
        self.num_boards = num_boards
        self.boards = boards

class BoardEntry (object) :
    def __init__ (self,
                  rnd, table,
                  ns, ns_score, ns_mp,
                  ew, ew_score, ew_mp) :
        self.round_num = rnd
        self.table_num = table
        self.ns_pair = ns
        self.ns_score = ns_score
        self.ns_mp_score = ns_mp
        self.ew_pair = ew
        self.ew_score = ew_score
        self.ew_mp_score = ew_mp

class BoardResults (object) :
    def __init__ (self,
                  board_id, comp_units, num_results,
                  entries) :
        self.board_id = board_id
        self.num_competitive_units = comp_units
        self.num_valid_results = num_results
        self.entries = entries

    def set_travellers (self, t) :
        self.travellers = t

    def set_board_num (self, n) :
        if (n != self.board_id) :
            print ('Warning board id from results and index structures are different ' +
                   str (self.board_id) + " != " +
                   str (n))
        self.board_num = n

    def set_num_results (self, n) :
        self.num_results = n
        

class MitchellPair (object) :
    def __init__ (self) :
        self.reassigned_pairs = []
        self.initial_table = []

    def add_reassignment (self, pairs) :
        self.reassigned_pairs.append(pairs)

    def add_initial (self, pairs) :
        self.initial_table.append(pairs)

class HowellPair (object) :
    def __init__ (self) :
        self.reassigned_pairs = []
        self.initial_table = []

    def add_reassignment (self, pairs) :
        self.reassigned_pairs.append(pairs)

    def add_initial (self, pairs) :
        self.initial_table.append(pairs)


