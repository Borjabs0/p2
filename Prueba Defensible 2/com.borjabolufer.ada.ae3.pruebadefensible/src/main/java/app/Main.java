package app;

import app.ApplicationService;
import util.DataInitializer;


public class Main {
	public static void main(String[] args) throws Exception {
		ApplicationService appService = new ApplicationService();
		Menu menu = new Menu(appService);
		DataInitializer initializer = new DataInitializer();

		initializer.initializeData();
		menu.mostrarMenuPrincipal();
	}
}