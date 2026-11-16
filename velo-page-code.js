// Wix Velo page code for the Partnership Feed page (Dev Mode on).
// Replace HTML_ID with the ID of the feed's HTML iframe element (Properties panel > ID), e.g. '#html1'.
import wixWindowFrontend from 'wix-window-frontend';

const HTML_ID = '#html1';

$w.onReady(function () {
  const feed = $w(HTML_ID);
  feed.onMessage((event) => {
    const d = event.data || {};
    if (d.type === 'GC_OPEN_SUBSCRIBE') {
      wixWindowFrontend.openLightbox('Partnership Digest popup');
    }
    // Auto-resize the iframe (feed posts FEED_HEIGHT)
    if (d.type === 'FEED_HEIGHT' && d.height) {
      feed.height = Math.ceil(d.height);
    }
  });
});
