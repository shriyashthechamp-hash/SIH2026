import camera01 from "@/assets/camera-01.jpg";
import camera02 from "@/assets/camera-02.jpg";
import camera03 from "@/assets/camera-03.jpg";

export type CameraFeed = {
  id: string;
  location: string;
  time: string;
  image: string;
  state: "LIVE" | "MATCHED";
};

export const cameraFeeds: CameraFeed[] = [
  { id: "CAM-01", location: "WEST JUNCTION", time: "14:32:08", image: camera01, state: "LIVE" },
  { id: "CAM-02", location: "CENTRAL FLYOVER", time: "14:35:24", image: camera02, state: "MATCHED" },
  { id: "CAM-03", location: "EAST CROSSING", time: "14:39:02", image: camera03, state: "LIVE" },
];

export const demoEvents = [
  { time: "14:32:08", title: "VEHICLE DETECTED", detail: "CAM-01", accent: "vehicle" as const },
  { time: "14:32:11", title: "PLATE RECOGNIZED", detail: "MH20EE0943", accent: "plate" as const },
  { time: "14:35:24", title: "VEHICLE MATCHED", detail: "CAM-02", accent: "tracking" as const },
  { time: "14:39:02", title: "JOURNEY UPDATED", detail: "CAM-03", accent: "event" as const },
];