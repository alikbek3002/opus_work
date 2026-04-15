export const OPUS_WORK_BOT_USERNAME = "opus_work_bot";
export const OPUS_WORK_BOT_WEB_URL = `https://t.me/${OPUS_WORK_BOT_USERNAME}`;
export const OPUS_WORK_BOT_APP_URL = `tg://resolve?domain=${OPUS_WORK_BOT_USERNAME}`;

interface OpenTelegramLinkOptions {
    appUrl: string;
    webUrl?: string;
    fallbackDelayMs?: number;
}

export function openTelegramLink({
    appUrl,
    webUrl,
    fallbackDelayMs = 900,
}: OpenTelegramLinkOptions) {
    if (typeof window === "undefined") {
        return;
    }

    let fallbackTimer: number | null = null;

    const cleanup = () => {
        if (fallbackTimer !== null) {
            window.clearTimeout(fallbackTimer);
            fallbackTimer = null;
        }
        document.removeEventListener("visibilitychange", handleVisibilityChange);
        window.removeEventListener("pagehide", cleanup);
    };

    const handleVisibilityChange = () => {
        if (document.visibilityState === "hidden") {
            cleanup();
        }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("pagehide", cleanup);

    fallbackTimer = window.setTimeout(() => {
        cleanup();

        if (webUrl) {
            window.location.assign(webUrl);
        }
    }, fallbackDelayMs);

    window.location.assign(appUrl);
}
