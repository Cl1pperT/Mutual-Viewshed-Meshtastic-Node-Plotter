export type ViewshedRequest = {
  observer: {
    lat: number;
    lon: number;
    heightMeters: number;
  };
  maxDistanceMeters: number;
  resolutionMeters: number;
};

export type ViewshedResponse = {
  // GeoJSON FeatureCollection describing visible area.
  visibleArea: unknown;
};
