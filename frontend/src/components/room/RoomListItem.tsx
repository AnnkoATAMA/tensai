import { ListItem, ListItemText, Button } from "@mui/material";
import { joinRoom } from "../../utils/roomApi";
import { useNavigate } from "react-router-dom";

interface RoomType {
    id: number;
    max_players: number;
    game_type: string;
}

const RoomListItem: React.FC<RoomType> = ({ id, max_players, game_type }) => {
    const navigate = useNavigate();

    const handleJoinRoom = async (roomId: number) => {
        try {
            await joinRoom(roomId);
            console.log(`部屋 ${roomId} に参加しました`);
            navigate(`/room/${roomId}`);
        } catch (err) {
            console.error("部屋の参加に失敗:", err);
        }
    };

    return (
        <ListItem sx={{ display: "flex", justifyContent: "space-between" }}>
            <ListItemText
                primary={`部屋ID: ${id}`}
                secondary={`最大プレイヤー: ${max_players}, ゲームタイプ: ${game_type}`}
            />
            <Button variant="contained" color="success" onClick={() => handleJoinRoom(id)}>
                参加
            </Button>
        </ListItem>
    );
};

export default RoomListItem;
