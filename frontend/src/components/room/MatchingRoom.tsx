import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Container, List, ListItem, ListItemText, Typography, Button, Card, Grid, Dialog, DialogTitle, DialogContent } from "@mui/material";
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


    return (
        <Container sx={{ mt: 4 }}>
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
                <Card sx={{ padding: 2, maxWidth: 600, margin: "auto", mt: 4 }}>
                    <Typography variant="h5">バイナリ麻雀</Typography>
                    <Grid container spacing={1}>
                        {binaryHand.map((binary, index) => (
                            <Grid item key={index}>
                                <Button
                                    variant="contained"
                                    color="secondary"
                                    sx={{ fontSize: "10px" }}
                                    onClick={() => sendAction("discard", { hai_idx: index })}
                                >
                                    {binary}
                                </Button>

                            </Grid>
                        ))}
                    </Grid>
                    <Button variant="contained" color="primary" onClick={() => sendAction("draw")} sx={{ mt: 2 }}>
                        ツモる
                    </Button>
                    <Button variant="contained" color="success" onClick={() => sendAction("claim_ron")} sx={{ mt: 2 }}>
                        ロン宣言
                    </Button>
                    <Button variant="contained" color="error" onClick={() => sendAction("claim_doubt", { target_id: roomId })} sx={{ mt: 2 }}>
                        ダウト宣言
                    </Button>
                    <Typography variant="body1" sx={{ mt: 2 }}>捨て牌: {discarded.join(", ")}</Typography>
                    {winner && <Typography variant="h6" sx={{ mt: 2 }}>勝者: {winner}</Typography>}
                    <Typography variant="h6" sx={{ mt: 2 }}>
                        捨て牌Box:
                    </Typography>
                    {Object.entries(binaryDiscarded).map(([playerId]) => (
                        <Button
                            key={playerId}
                            variant="contained"
                            color="primary"
                            sx={{ margin: 1 }}
                            onClick={() => handleOpenDiscard(playerId)}
                        >
                            {`プレイヤー ${playerId}` }
                        </Button>
                    ))}

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
        </Container>
    );
};
//
export default MatchingRoom;
