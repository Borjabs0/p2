package com.borjabolufer.ada.ae3.pruebadefensible.dao;

import java.util.List;

import org.hibernate.Session;
import org.hibernate.Transaction;

import com.borjabolufer.ada.ae3.pruebadefensible.dao.exceptions.DatabaseException;

import entities.Car;
import entities.Person;
import jakarta.persistence.TypedQuery;
import util.HibernateSessionFactory;

public class CarDAO{

	private static CarDAO instance = new CarDAO();
	
	public CarDAO() {
		// TODO Auto-generated constructor stub
	}

	public static CarDAO getInstance() {
		return instance;
	}



	public void addCar(Car car) throws DatabaseException {
		Transaction tx = null;
		try {
			Session session = HibernateSessionFactory.getSessionSingleton();
			tx = session.beginTransaction();
			session.persist(car);
			tx.commit();
		} catch (Exception e) {
			if (tx != null) {
				tx.rollback();
			}else {
				throw new DatabaseException(e.getMessage(), e);
			}
		}
	}

	public Car findById(String id) {
		Session session = HibernateSessionFactory.getSessionSingleton();
		return session.get(Car.class, id);
	}

	public List<Car> loadAllCars() throws DatabaseException {
		try {
			Session session = HibernateSessionFactory.getSessionSingleton();
			session.clear();
			TypedQuery<Car> query = session.createNativeQuery("SELECT * FROM Car_bb04", Car.class);
			List<Car> cars = query.getResultList();
			return cars;
		} catch (Exception e) {
			throw new DatabaseException(e.getMessage(), e);
		}
	}

}
