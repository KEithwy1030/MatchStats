const { createApp, ref, computed, onMounted, watch } = Vue;

const app = createApp({
    setup() {
        // State
        const loading = ref(false);
        const stats = ref({ fd_matches: 0, sporttery_matches: 0, last_sync: null });
        const matches = ref([]);
        const standings = ref([]);
        const logs = ref([]);

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
                stats.value = res.data;
            } catch (e) {
                console.error("Stats error", e);
            }
        };

        const fetchLogs = async () => {
            try {
                const res = await axios.get('/api/v1/logs?limit=20');
                logs.value = res.data.data;
            } catch (e) {
                console.error("Logs error", e);
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
            try {
                const isFd = activeSource.value === 'fd';
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
                matches.value = res.data.data || [];

                // Set default sporttery date to latest if not set or not in current list
                if (!isFd && sportteryDates.value.length > 0) {
                    if (!activeSportteryDate.value || !sportteryDates.value.includes(activeSportteryDate.value)) {
                        activeSportteryDate.value = sportteryDates.value[0];
                    }
                }
            } catch (e) {
                console.error("Matches error", e);
                matches.value = [];
            } finally {
                loading.value = false;
            }
        };

        const scorers = ref([]);
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
                const data = res.data.data || [];
                console.log(`Fetched ${data.length} standings items for ${activeLeague.value}`);
                standings.value = data;
            } catch (e) {
                console.error("Standings error", e);
                standings.value = [];
            }
        };

        const fetchScorers = async () => {
            if (activeSource.value !== 'fd' || activeLeague.value === 'ALL') {
                scorers.value = [];
                return;
            }
            try {
                const orderBy = activeTab.value === 'assists' ? 'assists' : 'goals';
                const res = await axios.get(`/api/v1/fd/leagues/${activeLeague.value}/scorers`, {
                    params: { order_by: orderBy, lang: 'zh' }
                });
                const data = res.data.data || [];
                scorers.value = data;
            } catch (e) {
                console.error("Scorers error", e);
                scorers.value = [];
            }
        };

        const refreshAll = () => {
            fetchStats();
            fetchMatches();
            fetchLogs();

            if (activeSource.value === 'fd') {
                fetchStandings();
                fetchScorers();
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
            refreshAll();
            setInterval(refreshAll, 60000);
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
