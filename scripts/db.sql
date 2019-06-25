DROP TABLE IF EXISTS contact CASCADE;
CREATE TABLE contact (
  id serial PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  email VARCHAR(128) NOT NULL UNIQUE,
  first_name VARCHAR(64) DEFAULT '',
  last_name VARCHAR(64) DEFAULT ''
);

DROP TABLE IF EXISTS segment CASCADE;
CREATE TABLE segment (
  id serial PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE
);

DROP TABLE IF EXISTS segment_contact CASCADE;
CREATE TABLE segment_contact (
  contact_id serial NOT NULL,
  segment_id serial NOT NULL,
  PRIMARY KEY (segment_id, contact_id),
  CONSTRAINT segment_contact_contact_fk FOREIGN KEY (contact_id)
    REFERENCES contact (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT segment_contact_segment_fk FOREIGN KEY (segment_id)
    REFERENCES segment (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE CASCADE
);

DROP TABLE IF EXISTS email_template CASCADE;
CREATE TABLE email_template (
  id serial PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  template TEXT NOT NULL
);

DROP TABLE IF EXISTS email_request CASCADE;
CREATE TABLE email_request (
  id serial PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  template_id serial NOT NULL,
  segment_id serial NOT NULL,
  CONSTRAINT email_request_segment_fk FOREIGN KEY (segment_id)
    REFERENCES segment (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT email_request_template_fk FOREIGN KEY (template_id)
    REFERENCES email_template (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE CASCADE
);

DROP TABLE IF EXISTS job CASCADE;
CREATE TABLE job (
  id serial PRIMARY KEY,
  request_id serial NOT NULL,
  status VARCHAR(16) NOT NULL,
  contact_id serial NOT NULL,
  CONSTRAINT job_request_fk FOREIGN KEY (request_id)
    REFERENCES email_request (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT job_contact_fk FOREIGN KEY (contact_id)
    REFERENCES contact (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE CASCADE
);