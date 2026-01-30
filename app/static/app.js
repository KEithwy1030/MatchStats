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
        const activeLeague = ref('ALL');
        const matchFilter = ref('ALL'); // 'ALL', 'LIVE', 'FINISHED'

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
            'LIVE': '进行中',
            'IN_PLAY': '进行中',
            'PAUSED': '中场',
            'FINISHED': '完场',
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

        const fetchMatches = async () => {
            loading.value = true;
            try {
                let url = activeSource.value === 'fd'
                    ? '/api/v1/fd/matches'
                    : '/api/v1/sporttery/matches';

                const params = { limit: 100 };

                // Add League filter for FD
                if (activeSource.value === 'fd' && activeLeague.value && activeLeague.value !== 'ALL') {
                    params.league = activeLeague.value;
                }

                // Add Status filter
                if (matchFilter.value !== 'ALL') {
                    // Match UI filters to API query values
                    params.status = matchFilter.value;
                }

                const res = await axios.get(url, { params });
                matches.value = res.data.data || [];
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
            if (activeSource.value !== 'fd') {
                standings.value = [];
                return;
            }
            try {
                const res = await axios.get(`/api/v1/fd/leagues/${activeLeague.value}/standings`);
                const data = res.data.data || [];
                console.log(`Fetched ${data.length} standings items for ${activeLeague.value}`);
                standings.value = data;
            } catch (e) {
                console.error("Standings error", e);
                standings.value = [];
            }
        };

        const fetchScorers = async () => {
            if (activeSource.value !== 'fd') {
                scorers.value = [];
                return;
            }
            try {
                const orderBy = activeTab.value === 'assists' ? 'assists' : 'goals';
                const res = await axios.get(`/api/v1/fd/leagues/${activeLeague.value}/scorers`, {
                    params: { order_by: orderBy }
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
            if (activeSource.value !== 'fd') return;

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
                venue: null
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
                    activeMatchDetail.value = detail;
                }
            } catch (e) {
                console.error("Fetch detail error", e);
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
            standings,
            scorers,
            activeTab,
            logs,
            activeSource,
            activeLeague,
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
