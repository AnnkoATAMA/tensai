import { use, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Box, Button, Container, MenuItem, Select, Typography } from "@mui/material";
import { createRoom } from "../../utils/roomApi";

const RoomForm = () => {
    const [gameType, setGameType] = useState("yonma");
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    const handleCreateRoom = () => {
        const roomPromise = createRoom(gameType)
            .then((response) => {
                console.log("部屋作成成功");
                const roomId = response.data.id;
                navigate(`/room/${roomId}`);
            })
            .catch((err) => {
                console.error("部屋作成エラー:", err);
                setError("部屋の作成に失敗しました");
            });

        use(roomPromise);
    };

    return (
        <Container sx={{ mt: 4 }}>
            <Typography variant="h5" gutterBottom>
                部屋を作成
            </Typography>
            {error && <Typography color="error">{error}</Typography>}
            <Box>
                <Select
                    value={gameType}
                    onChange={(e) => setGameType(e.target.value)}
                    fullWidth
                    displayEmpty
                >
                    <MenuItem value="sanma">三麻</MenuItem>
                    <MenuItem value="yonma">四麻</MenuItem>
                </Select>
                <Button
                    fullWidth
                    variant="contained"
                    color="primary"
                    sx={{ mt: 2 }}
                    onClick={handleCreateRoom}
                >
                    作成
                </Button>
            </Box>
        </Container>
    );
};

export default RoomForm;
