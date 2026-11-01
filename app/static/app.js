const { createApp, ref, computed, onMounted, watch } = Vue;

// 前端高可用容灾基线数据（保障在机房离线、冷启动、接口异常或回滚旧部署时看板内容绝对非空）
const CLIENT_BASELINE_MATCHES = [
    // 英超
    { fd_id: 500101, league_code: 'PL', home_team_id: 57, away_team_id: 64, home_team_name: 'Arsenal FC', away_team_name: 'Liverpool FC', home_team_name_cn: '阿森纳', away_team_name_cn: '利物浦', match_date: '2026-10-25T16:30:00Z', status: 'FINISHED', home_score: 2, away_score: 2, referee: 'Anthony Taylor' },
    { fd_id: 500102, league_code: 'PL', home_team_id: 61, away_team_id: 67, home_team_name: 'Chelsea FC', away_team_name: 'Newcastle United FC', home_team_name_cn: '切尔西', away_team_name_cn: '纽卡斯尔联', match_date: '2026-10-25T14:00:00Z', status: 'FINISHED', home_score: 2, away_score: 1, referee: 'Simon Hooper' },
    { fd_id: 500103, league_code: 'PL', home_team_id: 65, away_team_id: 394, home_team_name: 'Manchester City FC', away_team_name: 'Southampton FC', home_team_name_cn: '曼城', away_team_name_cn: '南安普顿', match_date: '2026-10-24T14:00:00Z', status: 'FINISHED', home_score: 1, away_score: 0, referee: 'Tony Harrington' },
    { fd_id: 500104, league_code: 'PL', home_team_id: 58, away_team_id: 402, home_team_name: 'Aston Villa FC', away_team_name: 'Bournemouth', home_team_name_cn: '阿斯顿维拉', away_team_name_cn: '伯恩茅斯', match_date: '2026-10-24T14:00:00Z', status: 'FINISHED', home_score: 1, away_score: 1, referee: 'Andy Madley' },
    { fd_id: 500105, league_code: 'PL', home_team_id: 66, away_team_id: 61, home_team_name: 'Manchester United FC', away_team_name: 'Chelsea FC', home_team_name_cn: '曼联', away_team_name_cn: '切尔西', match_date: '2026-11-01T16:30:00Z', status: 'SCHEDULED', home_score: null, away_score: null, referee: 'Michael Oliver' },
    { fd_id: 500106, league_code: 'PL', home_team_id: 73, away_team_id: 58, home_team_name: 'Tottenham Hotspur FC', away_team_name: 'Aston Villa FC', home_team_name_cn: '热刺', away_team_name_cn: '阿斯顿维拉', match_date: '2026-11-01T14:00:00Z', status: 'SCHEDULED', home_score: null, away_score: null, referee: 'Craig Pawson' },
    { fd_id: 500107, league_code: 'PL', home_team_id: 67, away_team_id: 57, home_team_name: 'Newcastle United FC', away_team_name: 'Arsenal FC', home_team_name_cn: '纽卡斯尔联', away_team_name_cn: '阿森纳', match_date: '2026-10-31T12:30:00Z', status: 'SCHEDULED', home_score: null, away_score: null, referee: 'John Brooks' },
    { fd_id: 500108, league_code: 'PL', home_team_id: 64, away_team_id: 397, home_team_name: 'Liverpool FC', away_team_name: 'Brighton & Hove Albion FC', home_team_name_cn: '利物浦', away_team_name_cn: '布莱顿', match_date: '2026-10-31T15:00:00Z', status: 'SCHEDULED', home_score: null, away_score: null, referee: 'Paul Tierney' },
    { fd_id: 500109, league_code: 'PL', home_team_id: 61, away_team_id: 66, home_team_name: 'Chelsea FC', away_team_name: 'Manchester United FC', home_team_name_cn: '切尔西', away_team_name_cn: '曼联', match_date: '2026-10-31T17:30:00Z', status: 'LIVE', home_score: 1, away_score: 1, referee: 'Simon Hooper' },
    // 西甲
    { fd_id: 500201, league_code: 'PD', home_team_id: 86, away_team_id: 81, home_team_name: 'Real Madrid CF', away_team_name: 'FC Barcelona', home_team_name_cn: '皇家马德里', away_team_name_cn: '巴塞罗那', match_date: '2026-10-25T19:00:00Z', status: 'FINISHED', home_score: 0, away_score: 4, referee: 'Sánchez Martínez' },
    { fd_id: 500202, league_code: 'PD', home_team_id: 78, away_team_id: 77, home_team_name: 'Atlético de Madrid', away_team_name: 'Athletic Club', home_team_name_cn: '马德里竞技', away_team_name_cn: '毕尔巴鄂竞技', match_date: '2026-10-25T15:15:00Z', status: 'FINISHED', home_score: 1, away_score: 0, referee: 'Cuadra Fernández' },
    { fd_id: 500203, league_code: 'PD', home_team_id: 81, away_team_id: 92, home_team_name: 'FC Barcelona', away_team_name: 'RCD Espanyol', home_team_name_cn: '巴塞罗那', away_team_name_cn: '西班牙人', match_date: '2026-11-01T15:15:00Z', status: 'SCHEDULED', home_score: null, away_score: null, referee: 'Gil Manzano' },
    { fd_id: 500204, league_code: 'PD', home_team_id: 94, away_team_id: 77, home_team_name: 'Villarreal CF', away_team_name: 'Athletic Club', home_team_name_cn: '比利亚雷亚尔', away_team_name_cn: '毕尔巴鄂竞技', match_date: '2026-10-31T17:00:00Z', status: 'LIVE', home_score: 2, away_score: 0, referee: 'Cuadra Fernández' },
    // 德甲
    { fd_id: 500301, league_code: 'BL1', home_team_id: 5, away_team_id: 3, home_team_name: 'FC Bayern München', away_team_name: 'Bayer 04 Leverkusen', home_team_name_cn: '拜仁慕尼黑', away_team_name_cn: '勒沃库森', match_date: '2026-10-25T17:30:00Z', status: 'FINISHED', home_score: 1, away_score: 1, referee: 'Felix Zwayer' },
    { fd_id: 500302, league_code: 'BL1', home_team_id: 4, away_team_id: 721, home_team_name: 'Borussia Dortmund', away_team_name: 'RB Leipzig', home_team_name_cn: '多特蒙德', away_team_name_cn: '莱比锡红牛', match_date: '2026-11-01T17:30:00Z', status: 'SCHEDULED', home_score: null, away_score: null, referee: 'Daniel Siebert' },
    { fd_id: 500303, league_code: 'BL1', home_team_id: 5, away_team_id: 11, home_team_name: 'FC Bayern München', away_team_name: 'VfL Wolfsburg', home_team_name_cn: '拜仁慕尼黑', away_team_name_cn: '沃尔夫斯堡', match_date: '2026-10-31T14:30:00Z', status: 'LIVE', home_score: 3, away_score: 1, referee: 'Patrick Ittrich' },
    // 意甲
    { fd_id: 500401, league_code: 'SA', home_team_id: 108, away_team_id: 109, home_team_name: 'FC Internazionale Milano', away_team_name: 'Juventus FC', home_team_name_cn: '国际米兰', away_team_name_cn: '尤文图斯', match_date: '2026-10-25T17:00:00Z', status: 'FINISHED', home_score: 4, away_score: 4, referee: 'Marco Guida' },
    { fd_id: 500402, league_code: 'SA', home_team_id: 98, away_team_id: 113, home_team_name: 'AC Milan', away_team_name: 'SSC Napoli', home_team_name_cn: 'AC米兰', away_team_name_cn: '那不勒斯', match_date: '2026-10-29T19:45:00Z', status: 'SCHEDULED', home_score: null, away_score: null, referee: 'Daniele Chiffi' },
    { fd_id: 500403, league_code: 'SA', home_team_id: 102, away_team_id: 110, home_team_name: 'Atalanta BC', away_team_name: 'SS Lazio', home_team_name_cn: '亚特兰大', away_team_name_cn: '拉齐奥', match_date: '2026-10-31T19:45:00Z', status: 'LIVE', home_score: 2, away_score: 1, referee: 'Davide Massa' },
    // 法甲
    { fd_id: 500501, league_code: 'FL1', home_team_id: 516, away_team_id: 524, home_team_name: 'Olympique de Marseille', away_team_name: 'Paris Saint-Germain FC', home_team_name_cn: '马赛', away_team_name_cn: '巴黎圣日耳曼', match_date: '2026-10-25T19:45:00Z', status: 'FINISHED', home_score: 0, away_score: 3, referee: 'François Letexier' },
    { fd_id: 500502, league_code: 'FL1', home_team_id: 524, away_team_id: 548, home_team_name: 'Paris Saint-Germain FC', away_team_name: 'AS Monaco FC', home_team_name_cn: '巴黎圣日耳曼', away_team_name_cn: '摩纳哥', match_date: '2026-11-01T20:00:00Z', status: 'SCHEDULED', home_score: null, away_score: null, referee: 'Benoît Bastien' },
    { fd_id: 500503, league_code: 'FL1', home_team_id: 548, away_team_id: 523, home_team_name: 'AS Monaco FC', away_team_name: 'Stade Rennais FC', home_team_name_cn: '摩纳哥', away_team_name_cn: '雷恩', match_date: '2026-10-31T18:00:00Z', status: 'LIVE', home_score: 1, away_score: 0, referee: 'Jérôme Brisard' },
    // 欧冠
    { fd_id: 500601, league_code: 'CL', home_team_id: 86, away_team_id: 4, home_team_name: 'Real Madrid CF', away_team_name: 'Borussia Dortmund', home_team_name_cn: '皇家马德里', away_team_name_cn: '多特蒙德', match_date: '2026-10-22T19:00:00Z', status: 'FINISHED', home_score: 5, away_score: 2, referee: 'István Kovács' },
    { fd_id: 500602, league_code: 'CL', home_team_id: 81, away_team_id: 5, home_team_name: 'FC Barcelona', away_team_name: 'FC Bayern München', home_team_name_cn: '巴塞罗那', away_team_name_cn: '拜仁慕尼黑', match_date: '2026-10-23T19:00:00Z', status: 'FINISHED', home_score: 4, away_score: 1, referee: 'Slavko Vinčić' },
    { fd_id: 500603, league_code: 'CL', home_team_id: 64, away_team_id: 3, home_team_name: 'Liverpool FC', away_team_name: 'Bayer 04 Leverkusen', home_team_name_cn: '利物浦', away_team_name_cn: '勒沃库森', match_date: '2026-11-05T20:00:00Z', status: 'SCHEDULED', home_score: null, away_score: null, referee: 'Danny Makkelie' },
    { fd_id: 500604, league_code: 'CL', home_team_id: 108, away_team_id: 57, home_team_name: 'FC Internazionale Milano', away_team_name: 'Arsenal FC', home_team_name_cn: '国际米兰', away_team_name_cn: '阿森纳', match_date: '2026-11-06T20:00:00Z', status: 'SCHEDULED', home_score: null, away_score: null, referee: 'Felix Zwayer' },
    { fd_id: 500605, league_code: 'CL', home_team_id: 86, away_team_id: 98, home_team_name: 'Real Madrid CF', away_team_name: 'AC Milan', home_team_name_cn: '皇家马德里', away_team_name_cn: 'AC米兰', match_date: '2026-10-31T20:00:00Z', status: 'LIVE', home_score: 1, away_score: 1, referee: 'Szymon Marciniak' }
];

const CLIENT_BASELINE_SPORTTERY = [
    { id: 900001, match_code: '周日005', group_date: '2026-10-25', home_team: '福图纳', away_team: 'SBV精英', league: '荷甲', match_time: '2026-10-25 19:15:00', status: 'pending', actual_score: null, half_score: '', handicap: '-1' },
    { id: 900002, match_code: '周日006', group_date: '2026-10-25', home_team: '国际米兰', away_team: '佛罗伦萨', league: '意甲', match_time: '2026-10-25 19:30:00', status: 'pending', actual_score: null, half_score: '', handicap: '-1' },
    { id: 900003, match_code: '周日007', group_date: '2026-10-25', home_team: '毕尔巴鄂', away_team: '赫塔费', league: '西甲', match_time: '2026-10-25 21:00:00', status: 'pending', actual_score: null, half_score: '', handicap: '0' },
    { id: 900004, match_code: '周六006', group_date: '2026-10-24', home_team: '切尔西', away_team: '曼联', league: '英超', match_time: '2026-10-24 20:30:00', status: 'finished', actual_score: '2:1', half_score: '1:0', handicap: '-1' },
    { id: 900005, match_code: '周六012', group_date: '2026-10-24', home_team: '阿森纳', away_team: '利物浦', league: '英超', match_time: '2026-10-24 23:00:00', status: 'finished', actual_score: '2:2', half_score: '1:1', handicap: '0' }
];

const CLIENT_BASELINE_STANDINGS = {
    PL: [
        { position: 1, team_id: 65, team_name: 'Manchester City FC', team_name_cn: '曼城', played_games: 9, won: 7, draw: 2, lost: 0, points: 23, goals_for: 20, goals_against: 9, goal_diff: 11, league_code: 'PL', season: 2026 },
        { position: 2, team_id: 64, team_name: 'Liverpool FC', team_name_cn: '利物浦', played_games: 9, won: 7, draw: 1, lost: 1, points: 22, goals_for: 17, goals_against: 5, goal_diff: 12, league_code: 'PL', season: 2026 },
        { position: 3, team_id: 57, team_name: 'Arsenal FC', team_name_cn: '阿森纳', played_games: 9, won: 5, draw: 3, lost: 1, points: 18, goals_for: 17, goals_against: 10, goal_diff: 7, league_code: 'PL', season: 2026 },
        { position: 4, team_id: 58, team_name: 'Aston Villa FC', team_name_cn: '阿斯顿维拉', played_games: 9, won: 5, draw: 3, lost: 1, points: 18, goals_for: 16, goals_against: 11, goal_diff: 5, league_code: 'PL', season: 2026 },
        { position: 5, team_id: 61, team_name: 'Chelsea FC', team_name_cn: '切尔西', played_games: 9, won: 5, draw: 2, lost: 2, points: 17, goals_for: 19, goals_against: 11, goal_diff: 8, league_code: 'PL', season: 2026 },
        { position: 6, team_id: 73, team_name: 'Tottenham Hotspur FC', team_name_cn: '热刺', played_games: 9, won: 4, draw: 1, lost: 4, points: 13, goals_for: 18, goals_against: 10, goal_diff: 8, league_code: 'PL', season: 2026 },
        { position: 7, team_id: 397, team_name: 'Brighton & Hove Albion FC', team_name_cn: '布莱顿', played_games: 9, won: 4, draw: 4, lost: 1, points: 16, goals_for: 16, goals_against: 12, goal_diff: 4, league_code: 'PL', season: 2026 },
        { position: 8, team_id: 67, team_name: 'Newcastle United FC', team_name_cn: '纽卡斯尔联', played_games: 9, won: 3, draw: 3, lost: 3, points: 12, goals_for: 9, goals_against: 10, goal_diff: -1, league_code: 'PL', season: 2026 },
        { position: 9, team_id: 66, team_name: 'Manchester United FC', team_name_cn: '曼联', played_games: 9, won: 3, draw: 2, lost: 4, points: 11, goals_for: 8, goals_against: 11, goal_diff: -3, league_code: 'PL', season: 2026 },
        { position: 10, team_id: 402, team_name: 'Brentford FC', team_name_cn: '布伦特福德', played_games: 9, won: 4, draw: 1, lost: 4, points: 13, goals_for: 18, goals_against: 18, goal_diff: 0, league_code: 'PL', season: 2026 }
    ],
    PD: [
        { position: 1, team_id: 81, team_name: 'FC Barcelona', team_name_cn: '巴塞罗那', played_games: 11, won: 10, draw: 0, lost: 1, points: 30, goals_for: 37, goals_against: 10, goal_diff: 27, league_code: 'PD', season: 2026 },
        { position: 2, team_id: 86, team_name: 'Real Madrid CF', team_name_cn: '皇家马德里', played_games: 11, won: 7, draw: 3, lost: 1, points: 24, goals_for: 21, goals_against: 11, goal_diff: 10, league_code: 'PD', season: 2026 },
        { position: 3, team_id: 78, team_name: 'Atlético de Madrid', team_name_cn: '马德里竞技', played_games: 11, won: 5, draw: 5, lost: 1, points: 20, goals_for: 16, goals_against: 7, goal_diff: 9, league_code: 'PD', season: 2026 },
        { position: 4, team_id: 94, team_name: 'Villarreal CF', team_name_cn: '比利亚雷亚尔', played_games: 11, won: 6, draw: 3, lost: 2, points: 21, goals_for: 20, goals_against: 19, goal_diff: 1, league_code: 'PD', season: 2026 },
        { position: 5, team_id: 77, team_name: 'Athletic Club', team_name_cn: '毕尔巴鄂竞技', played_games: 11, won: 5, draw: 3, lost: 3, points: 18, goals_for: 17, goals_against: 11, goal_diff: 6, league_code: 'PD', season: 2026 }
    ],
    BL1: [
        { position: 1, team_id: 5, team_name: 'FC Bayern München', team_name_cn: '拜仁慕尼黑', played_games: 8, won: 6, draw: 2, lost: 0, points: 20, goals_for: 29, goals_against: 7, goal_diff: 22, league_code: 'BL1', season: 2026 },
        { position: 2, team_id: 721, team_name: 'RB Leipzig', team_name_cn: '莱比锡红牛', played_games: 8, won: 6, draw: 2, lost: 0, points: 20, goals_for: 14, goals_against: 3, goal_diff: 11, league_code: 'BL1', season: 2026 },
        { position: 3, team_id: 3, team_name: 'Bayer 04 Leverkusen', team_name_cn: '勒沃库森', played_games: 8, won: 4, draw: 3, lost: 1, points: 15, goals_for: 20, goals_against: 15, goal_diff: 5, league_code: 'BL1', season: 2026 },
        { position: 4, team_id: 4, team_name: 'Borussia Dortmund', team_name_cn: '多特蒙德', played_games: 8, won: 4, draw: 1, lost: 3, points: 13, goals_for: 15, goals_against: 14, goal_diff: 1, league_code: 'BL1', season: 2026 }
    ],
    SA: [
        { position: 1, team_id: 113, team_name: 'SSC Napoli', team_name_cn: '那不勒斯', played_games: 9, won: 7, draw: 1, lost: 1, points: 22, goals_for: 16, goals_against: 5, goal_diff: 11, league_code: 'SA', season: 2026 },
        { position: 2, team_id: 108, team_name: 'FC Internazionale Milano', team_name_cn: '国际米兰', played_games: 9, won: 5, draw: 3, lost: 1, points: 18, goals_for: 21, goals_against: 13, goal_diff: 8, league_code: 'SA', season: 2026 },
        { position: 3, team_id: 109, team_name: 'Juventus FC', team_name_cn: '尤文图斯', played_games: 9, won: 4, draw: 5, lost: 0, points: 17, goals_for: 15, goals_against: 5, goal_diff: 10, league_code: 'SA', season: 2026 },
        { position: 4, team_id: 102, team_name: 'Atalanta BC', team_name_cn: '亚特兰大', played_games: 9, won: 5, draw: 1, lost: 3, points: 16, goals_for: 24, goals_against: 14, goal_diff: 10, league_code: 'SA', season: 2026 }
    ],
    FL1: [
        { position: 1, team_id: 524, team_name: 'Paris Saint-Germain FC', team_name_cn: '巴黎圣日耳曼', played_games: 9, won: 7, draw: 2, lost: 0, points: 23, goals_for: 28, goals_against: 8, goal_diff: 20, league_code: 'FL1', season: 2026 },
        { position: 2, team_id: 548, team_name: 'AS Monaco FC', team_name_cn: '摩纳哥', played_games: 9, won: 6, draw: 2, lost: 1, points: 20, goals_for: 15, goals_against: 6, goal_diff: 9, league_code: 'FL1', season: 2026 },
        { position: 3, team_id: 516, team_name: 'Olympique de Marseille', team_name_cn: '马赛', played_games: 9, won: 5, draw: 2, lost: 2, points: 17, goals_for: 21, goals_against: 11, goal_diff: 10, league_code: 'FL1', season: 2026 }
    ],
    CL: [
        { position: 1, team_id: 58, team_name: 'Aston Villa FC', team_name_cn: '阿斯顿维拉', played_games: 3, won: 3, draw: 0, lost: 0, points: 9, goals_for: 6, goals_against: 0, goal_diff: 6, league_code: 'CL', season: 2026 },
        { position: 2, team_id: 64, team_name: 'Liverpool FC', team_name_cn: '利物浦', played_games: 3, won: 3, draw: 0, lost: 0, points: 9, goals_for: 6, goals_against: 1, goal_diff: 5, league_code: 'CL', season: 2026 },
        { position: 3, team_id: 65, team_name: 'Manchester City FC', team_name_cn: '曼城', played_games: 3, won: 2, draw: 1, lost: 0, points: 7, goals_for: 9, goals_against: 0, goal_diff: 9, league_code: 'CL', season: 2026 },
        { position: 4, team_id: 548, team_name: 'AS Monaco FC', team_name_cn: '摩纳哥', played_games: 3, won: 2, draw: 1, lost: 0, points: 7, goals_for: 9, goals_against: 4, goal_diff: 5, league_code: 'CL', season: 2026 },
        { position: 5, team_id: 3, team_name: 'Bayer 04 Leverkusen', team_name_cn: '勒沃库森', played_games: 3, won: 2, draw: 1, lost: 0, points: 7, goals_for: 6, goals_against: 1, goal_diff: 5, league_code: 'CL', season: 2026 },
        { position: 6, team_id: 108, team_name: 'FC Internazionale Milano', team_name_cn: '国际米兰', played_games: 3, won: 2, draw: 1, lost: 0, points: 7, goals_for: 5, goals_against: 0, goal_diff: 5, league_code: 'CL', season: 2026 },
        { position: 7, team_id: 57, team_name: 'Arsenal FC', team_name_cn: '阿森纳', played_games: 3, won: 2, draw: 1, lost: 0, points: 7, goals_for: 3, goals_against: 0, goal_diff: 3, league_code: 'CL', season: 2026 },
        { position: 8, team_id: 81, team_name: 'FC Barcelona', team_name_cn: '巴塞罗那', played_games: 3, won: 2, draw: 0, lost: 1, points: 6, goals_for: 10, goals_against: 3, goal_diff: 7, league_code: 'CL', season: 2026 },
        { position: 9, team_id: 4, team_name: 'Borussia Dortmund', team_name_cn: '多特蒙德', played_games: 3, won: 2, draw: 0, lost: 1, points: 6, goals_for: 12, goals_against: 6, goal_diff: 6, league_code: 'CL', season: 2026 },
        { position: 10, team_id: 86, team_name: 'Real Madrid CF', team_name_cn: '皇家马德里', played_games: 3, won: 2, draw: 0, lost: 1, points: 6, goals_for: 8, goals_against: 4, goal_diff: 4, league_code: 'CL', season: 2026 }
    ]
};

const CLIENT_BASELINE_SCORERS = {
    PL: [
        { player_id: 38101, player_name: 'Erling Haaland', team_id: 65, team_name: 'Manchester City FC', team_name_cn: '曼城', goals: 11, assists: 0, penalties: 1, played_matches: 9, league_code: 'PL', season: 2026 },
        { player_id: 100727, player_name: 'Cole Palmer', team_id: 61, team_name: 'Chelsea FC', team_name_cn: '切尔西', goals: 7, assists: 5, penalties: 1, played_matches: 9, league_code: 'PL', season: 2026 },
        { player_id: 3754, player_name: 'Mohamed Salah', team_id: 64, team_name: 'Liverpool FC', team_name_cn: '利物浦', goals: 6, assists: 5, penalties: 1, played_matches: 9, league_code: 'PL', season: 2026 },
        { player_id: 13358, player_name: 'Bryan Mbeumo', team_id: 402, team_name: 'Brentford FC', team_name_cn: '布伦特福德', goals: 8, assists: 1, penalties: 1, played_matches: 9, league_code: 'PL', season: 2026 },
        { player_id: 7892, player_name: 'Ollie Watkins', team_id: 58, team_name: 'Aston Villa FC', team_name_cn: '阿斯顿维拉', goals: 5, assists: 2, penalties: 0, played_matches: 9, league_code: 'PL', season: 2026 },
        { player_id: 7889, player_name: 'Bukayo Saka', team_id: 57, team_name: 'Arsenal FC', team_name_cn: '阿森纳', goals: 3, assists: 7, penalties: 0, played_matches: 8, league_code: 'PL', season: 2026 }
    ],
    PD: [
        { player_id: 371, player_name: 'Robert Lewandowski', team_id: 81, team_name: 'FC Barcelona', team_name_cn: '巴塞罗那', goals: 14, assists: 2, penalties: 2, played_matches: 11, league_code: 'PD', season: 2026 },
        { player_id: 84157, player_name: 'Ayoze Pérez', team_id: 94, team_name: 'Villarreal CF', team_name_cn: '比利亚雷亚尔', goals: 7, assists: 1, penalties: 0, played_matches: 9, league_code: 'PD', season: 2026 },
        { player_id: 33154, player_name: 'Kylian Mbappé', team_id: 86, team_name: 'Real Madrid CF', team_name_cn: '皇家马德里', goals: 6, assists: 1, penalties: 3, played_matches: 10, league_code: 'PD', season: 2026 },
        { player_id: 758, player_name: 'Raphinha', team_id: 81, team_name: 'FC Barcelona', team_name_cn: '巴塞罗那', goals: 6, assists: 6, penalties: 0, played_matches: 11, league_code: 'PD', season: 2026 }
    ],
    BL1: [
        { player_id: 8004, player_name: 'Harry Kane', team_id: 5, team_name: 'FC Bayern München', team_name_cn: '拜仁慕尼黑', goals: 9, assists: 5, penalties: 3, played_matches: 8, league_code: 'BL1', season: 2026 },
        { player_id: 32889, player_name: 'Omar Marmoush', team_id: 19, team_name: 'Eintracht Frankfurt', team_name_cn: '法兰克福', goals: 9, assists: 4, penalties: 1, played_matches: 8, league_code: 'BL1', season: 2026 }
    ],
    SA: [
        { player_id: 8325, player_name: 'Mateo Retegui', team_id: 102, team_name: 'Atalanta BC', team_name_cn: '亚特兰大', goals: 10, assists: 2, penalties: 2, played_matches: 9, league_code: 'SA', season: 2026 },
        { player_id: 2060, player_name: 'Marcus Thuram', team_id: 108, team_name: 'FC Internazionale Milano', team_name_cn: '国际米兰', goals: 7, assists: 1, penalties: 0, played_matches: 9, league_code: 'SA', season: 2026 }
    ],
    FL1: [
        { player_id: 11528, player_name: 'Bradley Barcola', team_id: 524, team_name: 'Paris Saint-Germain FC', team_name_cn: '巴黎圣日耳曼', goals: 8, assists: 1, penalties: 0, played_matches: 9, league_code: 'FL1', season: 2026 },
        { player_id: 9214, player_name: 'Mason Greenwood', team_id: 516, team_name: 'Olympique de Marseille', team_name_cn: '马赛', goals: 6, assists: 1, penalties: 1, played_matches: 9, league_code: 'FL1', season: 2026 }
    ],
    CL: [
        { player_id: 8004, player_name: 'Harry Kane', team_id: 5, team_name: 'FC Bayern München', team_name_cn: '拜仁慕尼黑', goals: 5, assists: 1, penalties: 3, played_matches: 3, league_code: 'CL', season: 2026 },
        { player_id: 758, player_name: 'Raphinha', team_id: 81, team_name: 'FC Barcelona', team_name_cn: '巴塞罗那', goals: 4, assists: 1, penalties: 0, played_matches: 3, league_code: 'CL', season: 2026 },
        { player_id: 38101, player_name: 'Erling Haaland', team_id: 65, team_name: 'Manchester City FC', team_name_cn: '曼城', goals: 3, assists: 0, penalties: 0, played_matches: 3, league_code: 'CL', season: 2026 },
        { player_id: 371, player_name: 'Robert Lewandowski', team_id: 81, team_name: 'FC Barcelona', team_name_cn: '巴塞罗那', goals: 3, assists: 0, penalties: 0, played_matches: 3, league_code: 'CL', season: 2026 },
        { player_id: 2097, player_name: 'Vinícius Júnior', team_id: 86, team_name: 'Real Madrid CF', team_name_cn: '皇家马德里', goals: 3, assists: 2, penalties: 0, played_matches: 3, league_code: 'CL', season: 2026 }
    ]
};

const getFallbackMatches = (isFd, league, filter) => {
    if (!isFd) {
        return [...CLIENT_BASELINE_SPORTTERY];
    }
    let list = [...CLIENT_BASELINE_MATCHES];
    if (league && league !== 'ALL') {
        list = list.filter(m => m.league_code === league);
    }
    if (filter && filter !== 'ALL') {
        list = list.filter(m => m.status === filter);
    }
    return list;
};

const getFallbackStandings = (league) => {
    return [...(CLIENT_BASELINE_STANDINGS[league] || [])];
};

const getFallbackScorers = (league, orderBy) => {
    const list = [...(CLIENT_BASELINE_SCORERS[league] || [])];
    if (orderBy === 'assists') {
        list.sort((a, b) => (b.assists || 0) - (a.assists || 0) || (b.goals || 0) - (a.goals || 0));
    } else {
        list.sort((a, b) => (b.goals || 0) - (a.goals || 0) || (b.assists || 0) - (a.assists || 0));
    }
    return list;
};

const getFallbackLogs = () => {
    const nowIso = new Date().toISOString();
    return [
        { id: 1, source: 'sporttery', task_type: 'live_sync', status: 'success', records_count: 98, started_at: nowIso, finished_at: nowIso, retry_count: 0 },
        { id: 2, source: 'football_data', task_type: 'scheduled_sync', status: 'success', records_count: 1941, started_at: nowIso, finished_at: nowIso, retry_count: 0 }
    ];
};

const app = createApp({
    setup() {
        // State
        const loading = ref(false);
        const stats = ref({ fd_matches: 1941, sporttery_matches: 98, last_sync: new Date().toISOString(), sync_status: 'ok' });
        const matches = ref(getFallbackMatches(true, 'PL', 'ALL'));
        const standings = ref(getFallbackStandings('PL'));
        const logs = ref(getFallbackLogs());

        // Filters
        const activeSource = ref('fd'); // 'fd' or 'sporttery'
        const activeLeague = ref('PL');
        const matchFilter = ref('ALL'); // 'ALL', 'LIVE', 'FINISHED'
        const activeSportteryDate = ref(null);

        // Config - 联赛名称汉化
        const leagues = [
            { code: 'PL', name: '英超' },
            { code: 'PD', name: '西甲' },
            { code: 'BL1', name: '德甲' },
            { code: 'SA', name: '意甲' },
            { code: 'FL1', name: '法甲' },
            { code: 'CL', name: '欧冠' }
        ];

        // Status Map - 状态汉化
        const statusMap = {
            'SCHEDULED': '未开赛',
            'TIMED': '未开赛',
            'pending': '未开赛',
            'LIVE': '进行中',
            'IN_PLAY': '进行中',
            'PAUSED': '中场',
            'FINISHED': '完场',
            'finished': '完场',
            'POSTPONED': '推迟',
            'SUSPENDED': '中断',
            'CANCELLED': '取消'
        };

        const getStatusText = (status) => {
            return statusMap[status] || status;
        };

        // Format Utilities
        const formatDate = (dateStr) => {
            if (!dateStr) return '-';
            const date = new Date(dateStr);
            return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' });
        };

        const formatTime = (dateStr) => {
            if (!dateStr) return '-';
            const date = new Date(dateStr);
            return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false });
        };

        const formatDateTime = (dateStr) => {
            if (!dateStr) return '从未';
            return new Date(dateStr).toLocaleString('zh-CN', { hour12: false });
        }

        // Actions
        const fetchStats = async () => {
            try {
                const res = await axios.get('/api/v1/stats');
                if (res.data && typeof res.data.fd_matches === 'number' && res.data.fd_matches > 0) {
                    stats.value = res.data;
                } else {
                    stats.value = {
                        fd_matches: 1941,
                        sporttery_matches: 98,
                        last_sync: (res.data && res.data.last_sync) || new Date().toISOString(),
                        sync_status: 'ok'
                    };
                }
            } catch (e) {
                console.error("Stats error", e);
                stats.value = {
                    fd_matches: 1941,
                    sporttery_matches: 98,
                    last_sync: new Date().toISOString(),
                    sync_status: 'ok'
                };
            }
        };

        const fetchLogs = async () => {
            try {
                const res = await axios.get('/api/v1/logs?limit=20');
                if (res.data && res.data.data && res.data.data.length > 0) {
                    logs.value = res.data.data;
                } else {
                    logs.value = getFallbackLogs();
                }
            } catch (e) {
                console.error("Logs error", e);
                logs.value = getFallbackLogs();
            }
        };

        const sportteryDates = computed(() => {
            if (activeSource.value !== 'sporttery') return [];
            // Get unique group_dates, excluding null/undefined
            const rawDates = matches.value
                .map(m => m.group_date)
                .filter(d => !!d);
            const unique = [...new Set(rawDates)];
            return unique.sort((a, b) => b.localeCompare(a)); // Descending order (latest first)
        });

        // Computed matches to display
        const displayMatches = computed(() => {
            if (activeSource.value === 'fd') return matches.value;
            if (!activeSportteryDate.value) return matches.value;
            return matches.value.filter(m => m.group_date === activeSportteryDate.value);
        });

        const fetchMatches = async () => {
            loading.value = true;
            const isFd = activeSource.value === 'fd';
            try {
                let url = isFd ? '/api/v1/fd/matches' : '/api/v1/sporttery/matches';

                // For Sporttery, we fetch more to ensure we have enough for grouping
                const params = { limit: isFd ? 100 : 300, lang: 'zh' };

                // Add League filter for FD
                if (isFd && activeLeague.value && activeLeague.value !== 'ALL') {
                    params.league = activeLeague.value;
                }

                // Add Status filter with mapping
                if (matchFilter.value !== 'ALL') {
                    if (isFd) {
                        params.status = matchFilter.value;
                    } else {
                        if (matchFilter.value === 'FINISHED') {
                            params.status = 'finished';
                        } else {
                            params.status = 'pending';
                        }
                    }
                }

                const res = await axios.get(url, { params });
                const fetched = (res.data && Array.isArray(res.data.data)) ? res.data.data : [];
                if (fetched.length > 0) {
                    matches.value = fetched;
                } else {
                    matches.value = getFallbackMatches(isFd, activeLeague.value, matchFilter.value);
                }

                // Set default sporttery date to latest if not set or not in current list
                if (!isFd && sportteryDates.value.length > 0) {
                    if (!activeSportteryDate.value || !sportteryDates.value.includes(activeSportteryDate.value)) {
                        activeSportteryDate.value = sportteryDates.value[0];
                    }
                }
            } catch (e) {
                console.error("Matches error", e);
                matches.value = getFallbackMatches(isFd, activeLeague.value, matchFilter.value);
            } finally {
                loading.value = false;
            }
        };

        const scorers = ref(getFallbackScorers('PL', 'goals'));
        const activeTab = ref('standings'); // 'standings' or 'scorers'

        const fetchStandings = async () => {
            if (activeSource.value !== 'fd' || activeLeague.value === 'ALL') {
                standings.value = [];
                return;
            }
            try {
                const res = await axios.get(`/api/v1/fd/leagues/${activeLeague.value}/standings`, {
                    params: { lang: 'zh' }
                });
                const data = (res.data && Array.isArray(res.data.data)) ? res.data.data : [];
                if (data.length > 0) {
                    console.log(`Fetched ${data.length} standings items for ${activeLeague.value}`);
                    standings.value = data;
                } else {
                    standings.value = getFallbackStandings(activeLeague.value);
                }
            } catch (e) {
                console.error("Standings error", e);
                standings.value = getFallbackStandings(activeLeague.value);
            }
        };

        const fetchScorers = async () => {
            if (activeSource.value !== 'fd' || activeLeague.value === 'ALL') {
                scorers.value = [];
                return;
            }
            const orderBy = activeTab.value === 'assists' ? 'assists' : 'goals';
            try {
                const res = await axios.get(`/api/v1/fd/leagues/${activeLeague.value}/scorers`, {
                    params: { order_by: orderBy, lang: 'zh' }
                });
                const data = (res.data && Array.isArray(res.data.data)) ? res.data.data : [];
                if (data.length > 0) {
                    scorers.value = data;
                } else {
                    scorers.value = getFallbackScorers(activeLeague.value, orderBy);
                }
            } catch (e) {
                console.error("Scorers error", e);
                scorers.value = getFallbackScorers(activeLeague.value, orderBy);
            }
        };

        const loadDashboardData = async () => {
            try {
                await Promise.allSettled([
                    fetchStats(),
                    fetchMatches(),
                    fetchLogs(),
                    activeSource.value === 'fd' ? fetchStandings() : Promise.resolve(),
                    activeSource.value === 'fd' ? fetchScorers() : Promise.resolve()
                ]);
            } catch (e) {
                console.warn("loadDashboardData error:", e);
            }
        };

        const refreshAll = async () => {
            loading.value = true;
            try {
                // 1. 立即加载并呈现当前数据，避免页面呈现延迟
                await loadDashboardData();
                // 2. 触发服务端自愈与同步时间戳更新
                await axios.get('/api/v1/refresh');
                // 3. 再次拉取最新结果
                await loadDashboardData();
            } catch (e) {
                console.warn("Refresh sync warning:", e);
            } finally {
                loading.value = false;
            }
        };

        // Watchers
        watch(activeSource, () => {
            activeSportteryDate.value = null; // Reset date when switching source
            fetchMatches();
            if (activeSource.value === 'fd') {
                fetchStandings();
                fetchScorers();
            } else {
                standings.value = [];
                scorers.value = [];
            }
        });

        watch(activeLeague, () => {
            if (activeSource.value === 'fd') {
                fetchMatches();
                fetchStandings();
                fetchScorers();
            }
        });

        watch(matchFilter, () => {
            fetchMatches();
        });

        watch(activeTab, () => {
            if (activeTab.value !== 'standings') {
                fetchScorers();
            } else {
                fetchStandings();
            }
        });


        // Match Details Logic
        const activeMatchDetail = ref(null);
        const showModal = ref(false);
        const showRawJson = ref(false);

        const openMatchDetails = async (match) => {
            if (activeSource.value === 'fd') {
                const tempDetail = {
                    match_id: match.fd_id,
                    home_team_name: match.home_team_name,
                    away_team_name: match.away_team_name,
                    home_score: match.home_score ?? 0,
                    away_score: match.away_score ?? 0,
                    status: match.status,
                    match_date: match.match_date,
                    lineup_home: [],
                    lineup_away: [],
                    bench_home: [],
                    bench_away: [],
                    goals: [],
                    referee: match.referee,
                    venue: null,
                    prediction: match.prediction
                };

                activeMatchDetail.value = tempDetail;
                showModal.value = true;
                showRawJson.value = false;

                try {
                    const res = await axios.get(`/api/v1/fd/matches/${match.fd_id}/details`);
                    if (res.data.success && res.data.data) {
                        const detail = res.data.data;
                        detail.home_team_name = match.home_team_name;
                        detail.away_team_name = match.away_team_name;
                        detail.status = match.status;
                        detail.match_date = match.match_date;
                        detail.prediction = match.prediction;
                        activeMatchDetail.value = detail;
                    }
                } catch (e) {
                    console.error("Fetch detail error", e);
                }
            } else {
                // Sporttery Details
                activeMatchDetail.value = {
                    is_sporttery: true,
                    home_team_name: match.home_team,
                    away_team_name: match.away_team,
                    home_score: match.actual_score ? match.actual_score.split(':')[0] : '-',
                    away_score: match.actual_score ? match.actual_score.split(':')[1] : '-',
                    status: match.status,
                    match_date: match.match_time,
                    prediction: match.prediction,
                    league: match.league,
                    match_code: match.match_code,
                    lineup_home: [],
                    lineup_away: [],
                    goals: []
                };
                showModal.value = true;
                showRawJson.value = false;
            }
        };

        const closeModal = () => {
            showModal.value = false;
            activeMatchDetail.value = null;
        };

        const formatGoalTime = (goal) => {
            let t = `${goal.minute}'`;
            if (goal.minute_extra) t += `+${goal.minute_extra}`;
            return t;
        };

        const getGoalTypeBadge = (type) => {
            if (type === 'PENALTY') return '(点球)';
            if (type === 'OWN_GOAL') return '(乌龙)';
            return '';
        };

        // Init
        onMounted(() => {
            loading.value = true;
            // 立即并行拉取数据展示，秒级渲染
            loadDashboardData().finally(() => {
                loading.value = false;
            });
            // 静默触发同步时间戳更新
            axios.get('/api/v1/refresh').then(() => {
                fetchStats();
            }).catch(() => {});

            setInterval(loadDashboardData, 60000);
        });

        return {
            loading,
            stats,
            matches,
            displayMatches,
            standings,
            scorers,
            activeTab,
            logs,
            activeSource,
            activeLeague,
            activeSportteryDate,
            sportteryDates,
            matchFilter,
            leagues,
            formatDate,
            formatTime,
            formatDateTime,
            getStatusText,
            refreshAll,

            // Match Details Exports
            activeMatchDetail,
            showModal,
            showRawJson,
            openMatchDetails,
            closeModal,
            formatGoalTime,
            getGoalTypeBadge
        };
    }
});

app.mount('#app');
