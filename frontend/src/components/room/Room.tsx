import { use } from "react";
import { Container, List,Typography,} from "@mui/material";
import { fetchRooms,} from "../../utils/roomApi";
import RoomListItem from "./RoomListItem.tsx";

interface RoomType {
    id: number;
    max_players: number;
    game_type: string;
}

const roomListPromise = fetchRooms();

const Room = () => {
    const rooms: RoomType[] = use(roomListPromise);

    return (
        <Container sx={{ mt: 4 }}>
            <Typography variant="h5" gutterBottom>
                部屋一覧
            </Typography>
            <List>
                {rooms.map((room) => (
                    <RoomListItem key={room.id} id={room.id} max_players={room.max_players} game_type={room.game_type}/>
                ))}
            </List>
        </Container>
    );
};

export default Room;
