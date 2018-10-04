drop table nodes;
drop table nodes_tags;
drop table ways;
drop table ways_tags;
drop table ways_nodes;

create table nodes(
	id bigserial,
	lat numeric,
	lon numeric,
	user_name varchar(200),
	uid integer,
	version integer,
	changeset integer,
	timestamp timestamp,

	primary key(id)
);

create table nodes_tags(
	id bigserial,
	key varchar(200),
	type varchar(200),
	value varchar(200)
);

create table ways(
	id bigserial,
	user_name varchar(200),
	uid integer, 
	version integer,
	changeset integer, 
	timestamp timestamp
);

create table ways_tags(
	id bigserial, 
	key varchar(200),
	value varchar(2000), 
	type varchar(200)
);

create table ways_nodes(
	id bigserial,
	node_id bigserial, 
	position integer
);