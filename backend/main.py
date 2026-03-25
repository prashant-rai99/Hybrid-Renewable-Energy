from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib

from energy_optimizer import optimize_energy

app = FastAPI()

# ✅ CORS ADD KARO (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load models
solar_model = joblib.load("models/solar_model_plant1.pkl")
wind_model = joblib.load("models/wind_model_loc1.pkl")


@app.get("/")
def home():
    return {"message": "Energy API Running 🚀"}


@app.get("/predict-and-optimize")
def predict_and_optimize(
    irradiation: float,
    temp: float,
    module_temp: float,
    hour: int,
    wind_speed: float,
    pressure: float,
    demand: float,
    battery: float
):

    # solar
    solar = solar_model.predict(
        [[irradiation, temp, module_temp, hour]]
    )[0]

    # wind (6 features)
    wind = wind_model.predict([
        [
            wind_speed,
            wind_speed,
            wind_speed + 2,
            temp,
            60,
            hour
        ]
    ])[0]

    # optimization
    result = optimize_energy(solar, wind, demand, battery)

    return {
        "solar_prediction": float(solar),
        "wind_prediction": float(wind),
        "decision": result
    }