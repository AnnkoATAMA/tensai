import { CircularProgress } from "@mui/material";
import { Suspense } from "react";
import Room from "../components/room/Room.tsx";
import RoomForm from "../components/room/RoomForm.tsx";

const RoomPage = () => {
    return (
        <Suspense fallback={<CircularProgress />}>
            <RoomForm />
            <Room />
        </Suspense>
    );
};

export default RoomPage;
