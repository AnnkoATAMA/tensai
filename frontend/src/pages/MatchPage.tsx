import { Suspense } from "react";
import { CircularProgress } from "@mui/material";
import MatchingRoom from "../components/room/MatchingRoom.tsx";

const MatchPage = () => {
    return (
        <Suspense fallback={<CircularProgress />}>
            <MatchingRoom />
        </Suspense>
    );
};

export default MatchPage;
