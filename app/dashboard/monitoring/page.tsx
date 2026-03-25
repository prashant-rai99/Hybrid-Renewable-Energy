'use client';

import { useEffect, useState } from 'react';
import { getEnergyData } from '@/lib/utils';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { AlertCircle, CheckCircle2, Zap, Wind, Battery, Plug } from 'lucide-react';

const generateGaugeData = (value: number) => [
  { name: 'used', value: value, fill: '#10b981' },
  { name: 'remaining', value: 100 - value, fill: '#1f2937' },
];

export default function MonitoringPage() {

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

  // ✅ loading fix
  if (!energyData) {
    return (
      <div className="flex items-center justify-center h-screen text-white text-xl">
        Loading Monitoring Data...
      </div>
    );
  }

  // ✅ convert backend → UI format
  const mappedData = {
    solar: {
      current: energyData.solar_prediction,
      capacity: 1500,
      efficiency: 92,
      status: "Optimal",
    },
    wind: {
      current: energyData.wind_prediction,
      capacity: 800,
      efficiency: 85,
      status: "Good",
    },
    battery: {
      level: energyData.decision.battery_action.includes("Charge") ? 80 : 40,
    },
    grid: {
      import: energyData.decision.grid_usage,
      status: "Connected",
    },
  };

  // ✅ realtime chart
  const realtimeData = Array.from({ length: 12 }, (_, i) => ({
    time: `${i * 5}min`,
    solar: mappedData.solar.current + Math.random() * 50,
    wind: mappedData.wind.current + Math.random() * 30,
  }));

  const statusItems = [
    {
      title: 'Solar Panels',
      ...mappedData.solar,
      icon: Zap,
      color: '#fbbf24',
      bgColor: 'bg-yellow-500/10',
    },
    {
      title: 'Wind Turbines',
      ...mappedData.wind,
      icon: Wind,
      color: '#3b82f6',
      bgColor: 'bg-blue-500/10',
    },
    {
      title: 'Battery Storage',
      status: mappedData.battery.level > 50 ? 'Healthy' : 'Low',
      current: mappedData.battery.level,
      capacity: 100,
      efficiency: 95,
      icon: Battery,
      color: '#10b981',
      bgColor: 'bg-green-500/10',
    },
    {
      title: 'Grid Connection',
      status: mappedData.grid.status,
      current: mappedData.grid.import,
      capacity: 1000,
      efficiency: 99,
      icon: Plug,
      color: '#8b5cf6',
      bgColor: 'bg-purple-500/10',
    },
  ];

  return (
    <div className="space-y-8">

      <div>
        <h2 className="text-3xl font-bold mb-2">Energy Monitoring</h2>
        <p className="text-muted-foreground">Real-time monitoring of all systems</p>
      </div>

      {/* STATUS CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {statusItems.map((item, i) => {
          const Icon = item.icon;
          const gaugeData = generateGaugeData(item.current);
          const isHealthy = item.status === 'Optimal' || item.status === 'Good' || item.status === 'Healthy' || item.status === 'Connected';

          return (
            <Card key={i}>
              <CardHeader>
                <div className="flex justify-between">
                  <div className="flex gap-3">
                    <Icon className="w-6 h-6" />
                    <div>
                      <CardTitle>{item.title}</CardTitle>
                      <p className="text-xs">Status: {item.status}</p>
                    </div>
                  </div>
                  {isHealthy ? <CheckCircle2 /> : <AlertCircle />}
                </div>
              </CardHeader>

              <CardContent>
                <PieChart width={150} height={150}>
                  <Pie data={gaugeData} dataKey="value" innerRadius={40} outerRadius={60}>
                    {gaugeData.map((entry, index) => (
                      <Cell key={index} fill={entry.fill} />
                    ))}
                  </Pie>
                </PieChart>

                <p>Output: {item.current.toFixed(2)} kW</p>
                <p>Capacity: {item.capacity}</p>
                <p>Efficiency: {item.efficiency}%</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* CHART */}
      <Card>
        <CardHeader>
          <CardTitle>Real-time Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={realtimeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="solar" stroke="#fbbf24" />
              <Line type="monotone" dataKey="wind" stroke="#3b82f6" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* SUMMARY */}
      <Card>
        <CardHeader>
          <CardTitle>System Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Total Output: {(mappedData.solar.current + mappedData.wind.current).toFixed(2)} kW</p>
          <p>Battery: {mappedData.battery.level}%</p>
          <p>Grid Usage: {mappedData.grid.import}</p>
        </CardContent>
      </Card>

    </div>
  );
}