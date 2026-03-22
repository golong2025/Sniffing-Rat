let currentPage = 1; let perPage = 50; let currentMediaPage = 1; let mediaPerPage = 50; let flvPlayer = null;
const path = window.location.pathname;

async function fetchDashboardData() {
    const [mediaRes, statsRes, domainsRes, credsRes] = await Promise.all([
        fetch('/api/media?page=1&per_page=50'),
        fetch('/api/stats'),
        fetch('/api/top_domains'),
        fetch('/api/credentials')
    ]);
    const media = (await mediaRes.json()).media || [];
    updateMediaPreview(media);
}
// ... (Logic simplified for push)
function openImage(url) { document.getElementById('image-element').src = url; document.getElementById('image-modal').style.display='block'; }
function playVideo(url) { document.getElementById('video-modal').style.display='block'; /* Player logic */ }
document.addEventListener('DOMContentLoaded', () => { if(path==='/') fetchDashboardData(); });
