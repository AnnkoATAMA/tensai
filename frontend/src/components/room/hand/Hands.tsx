import { useRef, useEffect, useState } from "react";
import Webcam from "react-webcam";
import * as HandsModule from "@mediapipe/hands";
import { countExtendedFingers, drawHand } from "./handsUtil";
import { Box, Typography } from "@mui/material";

const tiles = ["1萬", "2萬", "3萬", "4萬", "5萬", "6萬", "7萬", "8萬", "9萬", "東", "南", "西", "北", "中"];

const Hands = ({ onSelectTile, onConfirmDiscard, onCancel }: {
    onSelectTile: (tile: string) => void,
    onConfirmDiscard: () => void,
    onCancel: () => void
}) => {
    const webcamRef = useRef<Webcam | null>(null);
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const handsRef = useRef<HandsModule.Hands | null>(null);
    const [isCameraReady, setIsCameraReady] = useState(false);
    const [intervalId, setIntervalId] = useState<number | null>(null);
    const fingerCountsBuffer = useRef<number[]>([]);

    useEffect(() => {
        console.log("🔄 HandsComponent: useEffect 開始");

        if (!handsRef.current) {
            console.log("✅ Hands インスタンス作成");
            handsRef.current = new HandsModule.Hands({
                locateFile: (file) => `/node_modules/@mediapipe/hands/${file}`,
            });

            handsRef.current.setOptions({
                maxNumHands: 2,
                modelComplexity: 1,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5,
            });

            handsRef.current.onResults((results: HandsModule.Results) => {
                console.log("📸 Hand detection 結果:", results);

                const canvas = canvasRef.current;
                const ctx = canvas?.getContext("2d");
                if (!ctx || !canvas || !webcamRef.current || !webcamRef.current.video) {
                    console.warn("⚠️ Canvas またはカメラが未準備");
                    return;
                }

                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(webcamRef.current.video, 0, 0, canvas.width, canvas.height);

                if (results.multiHandLandmarks?.length > 0) {
                    console.log("🖐️ 手のランドマーク取得");
                    drawHand(ctx, results.multiHandLandmarks);

                    let totalFingers = 0;
                    results.multiHandLandmarks.forEach((landmarks) => {
                        if (landmarks.length !== 21) return;
                        totalFingers += countExtendedFingers(landmarks);
                    });

                    console.log(`✋ 認識された指の本数 (合計): ${totalFingers}`);

                    fingerCountsBuffer.current.push(totalFingers);
                    if (fingerCountsBuffer.current.length > 5) {
                        fingerCountsBuffer.current.shift();
                    }

                    const mostCommonFingers = getMostFrequentValue(fingerCountsBuffer.current);
                    console.log(`🔍 安定化後の指の本数: ${mostCommonFingers}`);

                    if (mostCommonFingers >= 1 && mostCommonFingers <= 10) {
                        console.log(`✅ 選択された牌: ${tiles[mostCommonFingers - 1]}`);
                        onSelectTile(tiles[mostCommonFingers - 1]);
                    }

                    if (mostCommonFingers === 0) {
                        console.log("✊ グー検出 - 選択リセット");
                        onCancel();
                    }
                } else {
                    console.warn("⚠️ 手が検出されていません");
                }
            });
        }

        const checkCameraReady = window.setInterval(() => {
            if (webcamRef.current?.video && webcamRef.current.video.readyState === 4) {
                console.log("✅ カメラの準備完了");
                setIsCameraReady(true);
                clearInterval(checkCameraReady);
            }
        }, 500);

        return () => {
            handsRef.current?.close();
            clearInterval(checkCameraReady);
            if (intervalId) clearInterval(intervalId);
            console.log("🔻 HandsComponent クリーンアップ");
        };
    }, [onSelectTile, onConfirmDiscard, onCancel]);

    useEffect(() => {
        if (!isCameraReady) return;

        const id = window.setInterval(async () => {
            if (!webcamRef.current || !webcamRef.current.video || webcamRef.current.video.readyState !== 4) {
                console.warn("⚠️ カメラの準備が未完了 (readyState !== 4)");
                return;
            }

            try {
                console.log("📸 hands.send() 呼び出し");
                await handsRef.current?.send({ image: webcamRef.current.video });
            } catch (error) {
                console.error("❌ hands.send() エラー:", error);
                return;
            }
        }, 3000);

        setIntervalId(id);

        return () => clearInterval(id);
    }, [isCameraReady]);

    return (
        <Box>
            <Typography>手を動かして牌を選択</Typography>
            <Webcam
                ref={webcamRef}
                width={640}
                height={480}
                screenshotFormat="image/jpeg"
                onUserMedia={() => console.log("✅ Webカメラが起動しました")}
                onUserMediaError={(error) => console.error("❌ Webカメラエラー:", error)}
            />
            <canvas ref={canvasRef} width={640} height={480} />
        </Box>
    );
};

export default Hands;

const getMostFrequentValue = (arr: number[]): number => {
    const freqMap = arr.reduce((acc, num) => {
        acc[num] = (acc[num] || 0) + 1;
        return acc;
    }, {} as Record<number, number>);

    return Object.keys(freqMap)
        .map(Number)
        .reduce((a, b) => (freqMap[a] > freqMap[b] ? a : b));
};