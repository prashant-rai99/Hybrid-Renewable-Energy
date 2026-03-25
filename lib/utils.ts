import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export async function getEnergyData() {
  try {
    const res = await fetch(
      "http://127.0.0.1:8000/predict-and-optimize?irradiation=0.8&temp=32&module_temp=40&hour=13&wind_speed=6&pressure=1012&demand=50&battery=40"
    );

    const data = await res.json();
    return data;

  } catch (error) {
    console.error("API Error:", error);
    return null;
  }
}