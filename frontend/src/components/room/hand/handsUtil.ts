import { drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils";
import { HAND_CONNECTIONS, NormalizedLandmarkListList } from "@mediapipe/hands";

export const drawHand = (ctx: CanvasRenderingContext2D, handLandmarks: NormalizedLandmarkListList) => {
    if (!handLandmarks) {
        console.warn("⚠️ handLandmarks が見つからない");
        return;
    }

    ctx.strokeStyle = "red";
    ctx.lineWidth = 2;

    handLandmarks.forEach((landmarks) => {
        drawConnectors(ctx, landmarks, HAND_CONNECTIONS, { color: "#00FF00", lineWidth: 2 });
        drawLandmarks(ctx, landmarks, { color: "#FF0000", lineWidth: 2, radius: 3 });
    });

    console.log("🖊️ 手の描画完了");
};

export const countExtendedFingers = (landmarks: any): number => {
    let extendedFingers = 0;
    const fingers = [8, 12, 16, 20];

    fingers.forEach((fingerTip) => {
        if (landmarks[fingerTip].y < landmarks[fingerTip - 2].y) {
            extendedFingers++;
        }
    });

    if (landmarks[4].x > landmarks[3].x) {
        extendedFingers++;
    }

    console.log(`🔢 指の本数カウント: ${extendedFingers}`);
    return extendedFingers;
};


export const detectSingleFingerUp = (landmarks: any): number | null => {
    const fingers = [8, 12, 16, 20];
    let upFinger: number | null = null;

    fingers.forEach((fingerTip, index) => {
        if (landmarks[fingerTip].y < landmarks[fingerTip - 2].y) {
            if (upFinger === null) {
                upFinger = index;
            } else {
                upFinger = null;
            }
        }
    });

    if (landmarks[4].x > landmarks[3].x && upFinger === null) {
        return 0;
    }

    console.log(`🆙 立っている指の検出: ${upFinger}`);
    return upFinger;
};