'use client';

import { useEffect, useState } from 'react';
import { getEnergyData } from '@/lib/utils';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Cloud, Wind, Thermometer, Eye } from 'lucide-react';

export default function ForecastingPage() {

  const [energyData, setEnergyData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      const data = await getEnergyData();
      setEnergyData(data);
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);

    return () => clearInterval(interval);
  }, []);

  // ✅ loading
  if (!energyData) {
    return (
      <div className="flex items-center justify-center h-screen text-white text-xl">
        Loading Forecast...
      </div>
    );
  }

  // ✅ generate forecast data (demo AI prediction style)
  const forecastData = Array.from({ length: 24 }, (_, i) => {
    const solar = energyData.solar_prediction * Math.sin((i / 24) * Math.PI);
    const wind = energyData.wind_prediction + Math.random() * 10;
    const demand = energyData.decision.energy_used + Math.random() * 20;

    return {
      hour: i,
      solar: parseFloat(Math.max(0, solar).toFixed(2)),
      wind: parseFloat(wind.toFixed(2)),
      demand: parseFloat(demand.toFixed(2)),
    };
  });

  // dummy weather (optional)
  const weatherData = [
    { icon: Thermometer, label: 'Temperature', value: '32°C' },
    { icon: Cloud, label: 'Cloud Cover', value: '40%' },
    { icon: Wind, label: 'Wind Speed', value: '12 km/h' },
    { icon: Eye, label: 'Visibility', value: '10 km' },
  ];

  return (
    <div className="space-y-8">

      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold mb-2">Energy Forecasting</h2>
        <p className="text-muted-foreground">AI-based 24-hour prediction</p>
      </div>

      {/* Weather */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {weatherData.map((item, i) => {
          const Icon = item.icon;
          return (
            <Card key={i}>
              <CardContent className="pt-6 flex justify-between">
                <div>
                  <p className="text-sm">{item.label}</p>
                  <p className="text-xl font-bold">{item.value}</p>
                </div>
                <Icon />
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Solar */}
      <Card>
        <CardHeader>
          <CardTitle>Solar Forecast</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={forecastData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Area dataKey="solar" stroke="#fbbf24" fill="#fbbf24" />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Wind */}
      <Card>
        <CardHeader>
          <CardTitle>Wind Forecast</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={forecastData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Area dataKey="wind" stroke="#3b82f6" fill="#3b82f6" />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Combined */}
      <Card>
        <CardHeader>
          <CardTitle>Combined Forecast</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={forecastData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line dataKey="solar" stroke="#fbbf24" />
              <Line dataKey="wind" stroke="#3b82f6" />
              <Line dataKey="demand" stroke="#ef4444" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardHeader>
          <CardTitle>Hourly Data</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th>Hour</th>
                <th>Solar</th>
                <th>Wind</th>
                <th>Demand</th>
              </tr>
            </thead>
            <tbody>
              {forecastData.slice(0, 10).map((item, i) => (
                <tr key={i}>
                  <td>{item.hour}</td>
                  <td>{item.solar}</td>
                  <td>{item.wind}</td>
                  <td>{item.demand}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

    </div>
  );
}