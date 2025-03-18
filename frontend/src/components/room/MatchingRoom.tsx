import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
    List,
    ListItem,
    ListItemText,
    Typography,
    Button,
    Card,
    Grid,
    Dialog,
    DialogTitle,
    DialogContent,
    Box
} from "@mui/material";
import { fetchRoomPlayers, leaveRoom, deleteRoom } from "../../utils/roomApi";
import { PaiList } from "./PaiList.ts"

interface PlayerType {
    user_id: number;
    username: string;
}


const MatchingRoom = () => {
    const { roomId } = useParams<{ roomId: string }>();
    const navigate = useNavigate();
    const [players, setPlayers] = useState<PlayerType[]>([]);
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [hand, setHand] = useState<string[]>([]);
    const [discarded, setDiscarded] = useState<string[]>([]);
    const [winner, setWinner] = useState<string | null>(null);
    const [gameStarted, setGameStarted] = useState(false);
    const [discardedTiles, setDiscardedTiles] = useState<{ [key: string]: string[] }>({});
    const [openPlayer, setOpenPlayer] = useState<string | null>(null);
    const [ronPlayer, setRonPlayer] = useState<string | null>(null);
    useEffect(() => {
        if (!roomId) return;

        const WS_URL = `ws://172.20.10.2:8000/room/${roomId}/ws`;
        const ws = new WebSocket(WS_URL);
        setSocket(ws);

        ws.onopen = () => {
            console.log("WebSocket connected to", WS_URL);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("WebSocket Message:", data);

            if (data.action === "game_started") {
                setGameStarted(true);
                sendGetGameState(ws);
            }

            if (data.action === "game_state") {
                console.log("プレイヤー一覧:", data.game_state.players);

                const currentPlayerId = Object.keys(data.game_state.players).find(
                    (id) => Array.isArray(data.game_state.players[id]?.hand) && data.game_state.players[id].hand.length > 0
                );

                if (!currentPlayerId) {
                    console.warn("手牌を持つプレイヤーが見つかりませんでした。");
                    return;
                }
                if (data.game_state.ron_player) {
                    setRonPlayer(data.game_state.ron_player);
                } else {
                    console.log()
                }

                console.log("現在のプレイヤーID:", currentPlayerId);
                console.log("取得した手牌:", data.game_state.players[currentPlayerId]?.hand);

                setHand(data.game_state.players[currentPlayerId]?.hand ?? []);
                setDiscarded(data.game_state.players[currentPlayerId]?.discarded ?? []);
                setWinner(data.game_state.winner ?? null);
                const newDiscardedTiles: { [key: string]: string[] } = {};
                Object.keys(data.game_state.players).forEach((id) => {
                    newDiscardedTiles[id] = data.game_state.players[id]?.discarded ?? [];
                });
                setDiscardedTiles(newDiscardedTiles);
            }
            if (data.action === "hai_discarded") {
                const { last_action_player, last_discarded_hai } = data;

                setDiscardedTiles((prev) => ({
                    ...prev,
                    [last_action_player]: [...(prev[last_action_player] || []), last_discarded_hai],
                }));
            }


        };

        ws.onclose = (event) => {
            console.log("WebSocket connection closed:", event.reason);
        };

        const interval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ action: "get_game_state" }));
            }
        }, 1000);

        fetchRoomPlayers(Number(roomId)).then(setPlayers);

        return () => {
            clearInterval(interval);
            if (ws.readyState === WebSocket.OPEN) {
                ws.close();
            }
            setSocket(null);
        };
    }, [roomId]);

    const sendGetGameState = (ws: WebSocket) => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ action: "get_game_state" }));
        }
    };

    const handleStartGame = () => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ action: "start_game" }));
            console.log("ゲームスタート");
            setGameStarted(true);
        }
    };

    const handleLeaveRoom = async () => {
        try {
            await leaveRoom(Number(roomId));
            navigate("/room");
        } catch (err) {
            console.error("退出に失敗しました:", err);
        }
    };

    const handleDeleteRoom = async () => {
        try {
            await deleteRoom(Number(roomId));
            console.log(`部屋 ${roomId} を削除しました`);
            navigate("/room");
        } catch (err) {
            console.error("部屋の削除に失敗:", err);
        }
    };

    const handleOpenDiscard = (playerId: string) => {
        console.log(discarded)
        setOpenPlayer(playerId);
    };

    const handleCloseDiscard = () => {
        setOpenPlayer(null);
    };

    const sendAction = (action: string, payload: any = {}) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ action, ...payload }));
        }
    };

    const convertToBinaryHand = (hand: string[]) => {
        return hand.map(tile => {
            const found = PaiList.find(pai => pai.name === tile);
            return found ? found.binary : tile;
        });
    };
    const binaryHand = convertToBinaryHand(hand);

    const convertTobinaryDiscarded = (discardedTiles: { [key: string]: string[] }) => {
        const binaryDiscarded: { [key: string]: string[] } = {};

        Object.entries(discardedTiles).forEach(([playerId, tiles]) => {
            binaryDiscarded[playerId] = tiles.map(pai => {
                const found = PaiList.find(pais => pais.name === pai);
                return found ? found.binary : pai;
            });
        });

        return binaryDiscarded;
    };

    const binaryDiscarded = convertTobinaryDiscarded(discardedTiles);

    const directions = ["東", "西", "南", "北"] as const;
    type DirectionType = typeof directions[number];

    const positions: Record<DirectionType, { position: string; top?: string; bottom?: string; left?: string; right?: string; transform?: string }> = {
        東: { position: "absolute", right: "20%", top: "30%" },
        西: { position: "absolute", left: "20%", top: "30%" },
        南: { position: "absolute", bottom: "5%", left: "50%", transform: "translateX(-50%)" },
        北: { position: "absolute", top: "5%", left: "50%", transform: "translateX(-50%)" }
    };

    return (
        <Box sx={{ mt: 4 }}>
            <Typography variant="h5" gutterBottom>
                ルーム {roomId} - 参加者一覧
            </Typography>

            <List>
                {players.map((player) => (
                    <ListItem key={player.user_id}>
                        <ListItemText primary={player.username} />
                    </ListItem>
                ))}
            </List>

            {!gameStarted && (
                <Button variant="contained" color="primary" sx={{ mt: 2 }} onClick={handleStartGame}>
                    ゲーム開始
                </Button>
            )}

            <Button variant="contained" color="secondary" sx={{ mt: 2, ml: 2 }} onClick={handleLeaveRoom}>
                退出
            </Button>

            <Button variant="contained" color="error" sx={{ mt: 2, ml: 2 }} onClick={handleDeleteRoom}>
                部屋を削除
            </Button>

            {gameStarted && (
                <Card
                    sx={{
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "space-between",
                        padding: 2,
                        height: 1000,
                        maxWidth: 1800,
                        margin: "auto",
                        mt: 4,
                        background: "radial-gradient(#00633A, #014026)",
                        border: "8px solid",
                        borderImage: "radial-gradient(#83420c, #4e300a)49%",
                    }}
                >
                    <Typography variant="h5">バイナリ麻雀</Typography>

                    <Box sx={{ position: "relative", width: "100%", height: "400px", display: "flex", justifyContent: "center", alignItems: "center" }}>
                        {directions.map((direction, index) => {
                            const playerId = Object.keys(binaryDiscarded)[index];
                            return (
                                <Button
                                    key={direction}
                                    variant="contained"
                                    color="primary"
                                    sx={{ ...positions[direction] }}
                                    onClick={() => playerId && handleOpenDiscard(playerId)}
                                    disabled={!playerId}
                                >
                                    {direction}
                                </Button>
                            );
                        })}
                    </Box>
                    <Box sx={{ marginTop: "auto" }}>
                        <Grid container spacing={1} justifyContent="center">
                            {binaryHand.map((binary, index) => (
                                <Grid item key={index}>
                                    <Button
                                        variant="contained"
                                        sx={{
                                            fontSize: "10px",
                                            background: "linear-gradient(180deg, #e38010 0%, #e38010 10%, white 10%, white 90%)", // ✅ 閉じカッコを追加
                                            width: "97px",
                                            height: "180px",
                                            borderRadius: "5%",
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            color: "black",
                                            boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
                                            border: "2px solid black",
                                        }}
                                        onClick={() => sendAction("discard", { hai_idx: index })}
                                    >
                                        {binary}
                                    </Button>
                                </Grid>
                            ))}
                        </Grid>
                        <Button variant="contained" color="success" onClick={() => sendAction("claim_ron")} sx={{ mt: 2 }}>
                            宣言
                        </Button>
                        <Button
                            variant="contained"
                            color="error"
                            onClick={() => {
                                if (!ronPlayer) {
                                    console.warn("ダウト対象がいないため送信できません");
                                    return;
                                }
                                sendAction("claim_doubt", { target_id: ronPlayer });
                            }}
                            sx={{ mt: 2 }}
                        >
                            ダウト宣言
                        </Button>
                    </Box>
                    {winner && <Typography variant="h6" sx={{ mt: 2 }}>勝者: {winner}</Typography>}


                    <Dialog open={openPlayer !== null} onClose={handleCloseDiscard}>
                        <DialogTitle>{openPlayer ? `プレイヤー ${openPlayer} の捨て牌` : ""}</DialogTitle>
                        <DialogContent>
                            <Typography>
                                {openPlayer && binaryDiscarded[openPlayer] ? binaryDiscarded[openPlayer].join(", ") : "捨て牌なし"}
                            </Typography>
                        </DialogContent>
                    </Dialog>
                </Card>
            )}
        </Box>
    );
};

export default MatchingRoom;
