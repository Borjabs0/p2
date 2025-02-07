package util;

import java.util.logging.Level;

import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.cfg.Configuration;

public class HibernateSessionFactory {
	private static SessionFactory factory;
	private static Session sessionSingleton;

	static {
		buildSessionFactory();
	}

	private static void buildSessionFactory() {
		java.util.logging.Logger.getLogger("").setLevel(Level.SEVERE);
		try {
			// Create the SessionFactory from hibernate.cfg.xml
			factory = new Configuration().configure().buildSessionFactory();
			sessionSingleton = factory.openSession();
		} catch (Throwable ex) {
			// Make sure you log the exception, as it might be swallowed
			System.err.println("SessionFactory creation failed." + ex);
			throw new ExceptionInInitializerError(ex);
		}
	}

	private static SessionFactory getSessionFactory() {
		return factory;
	}

	public static Session getSessionSingleton() {
		return sessionSingleton;
	}

	public static void shutdown() {
		sessionSingleton.close();
		factory.close();
	}
}
