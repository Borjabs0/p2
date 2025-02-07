package util;

import com.borjabolufer.ada.ae3.pruebadefensible.dao.exceptions.DatabaseException;
import app.ApplicationService;

public class DataInitializer {
	private ApplicationService appService;

	public DataInitializer() {
		this.appService = new ApplicationService();
	}

	/**
	 * Inicializa la base de datos con datos de prueba
	 */
	public void initializeData() {
		try {
			if (!appService.isDataInitialized()) {
				insertPersons();

				insertCars();

				insertPolicies();

				insertAccidents();

				insertParticipations();
				System.out.println("Datos inicializados correctamente");
			} else {
				System.out.println("Los datos ya están inicializados. No se realizará ninguna acción.");
			}

		} catch (Exception e) {
			System.err.println("Error al inicializar los datos: " + e.getMessage());
			e.printStackTrace();
		}
	}

	private void insertPersons() throws DatabaseException {
		appService.addPerson("personA", "c/Pez 1°A", "Sergio Alejo");
		appService.addPerson("personB", "c/Pez 1°B", "Elia Bastian");
		appService.addPerson("personC", "c/Pez 1°C", "Juan Clade");
	}

	private void insertCars() throws Exception {
		appService.addCar("carA", "Ford Focus", 2011, "personA");
		appService.addCar("carB", "Seat Ibiza", 2012, "personA");
		appService.addCar("carC", "Renault Laguna", 2013, "personB");
		appService.addCar("carD", "Fiat Tipo", 2014, "personC");
	}

	private void insertPolicies() throws DatabaseException {
		appService.addPolicy("polA", "carA");
		appService.addPolicy("polB", "carB");
	}

	private void insertAccidents() throws DatabaseException {
		appService.addAccident("accA", "Madrid");
		appService.addAccident("accB", "Teruel");
		appService.addAccident("accC", "Lugo");
	}

	private void insertParticipations() throws DatabaseException {
		// Añadir participaciones en accidentes
		appService.addCarAccident("carA", "accA");
		appService.addCarAccident("carB", "accA");
		appService.addCarAccident("carC", "accB");
		appService.addCarAccident("carD", "accB");
		appService.addCarAccident("carA", "accC");
		appService.addCarAccident("carD", "accC");
	}
}