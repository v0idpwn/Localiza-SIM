PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS bus;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS schedules;
DROP TABLE IF EXISTS stops;

create table routes (
	route_id 		INTEGER PRIMARY KEY AUTOINCREMENT,
	route_name 		TEXT NOT NULL
);

create table schedules (
	sch_id			INTEGER PRIMARY KEY AUTOINCREMENT,
	route_fk 		INTEGER NOT NULL,
	sch_time 		TEXT NOT NULL,
	sch_begin 		TEXT NOT NULL,
	sch_end   		TEXT NOT NULL,
	sch_period		INTEGER NOT NULL,
	sch_bus			INTEGER NOT NULL,
	traj_id			INTEGER NOT NULL,
	sch_desc		TEXT,
	FOREIGN KEY(sch_bus)  REFERENCES bus(bus_id),
	FOREIGN KEY(route_fk) REFERENCES routes(route_id),
	FOREIGN KEY(traj_id) REFERENCES trajs(traj_id)
);


create table stops (
	stop_id			INTEGER PRIMARY KEY AUTOINCREMENT,
	stop_name		TEXT NOT NULL,
	stop_latitude	FLOAT NOT NULL,
	stop_longitude 	FLOAT NOT NULL
);

create table traj_stop (
	traj_id  		INTEGER NOT NULL,
	stop_id 	 	INTEGER NOT NULL,
	FOREIGN KEY(traj_id) REFERENCES trajs(traj_id),
	FOREIGN KEY(stop_id) REFERENCES stop(stop_id)
);

create table bus (
	bus_id 				INTEGER PRIMARY KEY AUTOINCREMENT,
	bus_name			TEXT NOT NULL
);

create table bus_data (
	bus_id 			INTEGER NOT NULL,
	data_id 		INTEGER PRIMARY KEY,
	last_longitude 	FLOAT NOT NULL,
	last_latitude 	FLOAT NOT NULL,
	last_time 		TEXT NOT NULL,
	FOREIGN KEY (bus_id) REFERENCES bus(bus_id)
);

create table trajs (
	traj_id				INTEGER PRIMARY KEY AUTOINCREMENT,
	traj_name			TEXT NOT NULL,
	traj_filename		TEXT NOT NULL UNIQUE
);
