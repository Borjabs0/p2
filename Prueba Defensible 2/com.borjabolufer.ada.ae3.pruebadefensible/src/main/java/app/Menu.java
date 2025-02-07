package app;

import java.util.Scanner;

import com.borjabolufer.ada.ae3.pruebadefensible.dao.exceptions.DatabaseException;
import com.google.protobuf.ValueOrBuilder;

import util.LibIO;

public class Menu {
	private ApplicationService appService;
	private Scanner scanner;

	public Menu(ApplicationService appService) {
		this.appService = appService;
		this.scanner = new Scanner(System.in);
	}

	public void mostrarMenuPrincipal() throws Exception {
		int opcion;
		do {
			System.out.println();
			System.out.println("╔══════════════════════════╗");
			System.out.println("║      MENÚ PRINCIPAL      ║");
			System.out.println("╠══════════════════════════╣");
			System.out.println("║  1. Gestionar Personas   ║");
			System.out.println("║  2. Gestionar Coches     ║");
			System.out.println("║  3. Gestionar Pólizas    ║");
			System.out.println("║  4. Gestionar Accidentes ║");
			System.out.println("╠══════════════════════════╣");
			System.out.println("║  0. Salir                ║");
			System.out.println("╚══════════════════════════╝");
			System.out.print("Seleccione una opción: ");
			opcion = scanner.nextInt();
			scanner.nextLine();

			switch (opcion) {
			case 1:
				gestionarPersonas();
				break;
			case 2:
				gestionarCoches();
				break;
			case 3:
				gestionarPolizas();
				break;
			case 4:
				gestionarAccidentes();
				break;
			case 0:
				System.out.println("Saliendo del programa...");
				break;
			default:
				System.out.println("Opción no válida.");
			}
		} while (opcion != 0);
	}

	private void gestionarPersonas() throws Exception {
		int opcion;
		do {
			System.out.println();
			System.out.println("╔══════════════════════════╗");
			System.out.println("║    GESTIÓN DE PERSONAS   ║");
			System.out.println("╠══════════════════════════╣");
			System.out.println("║  1. Añadir Persona       ║");
			System.out.println("║  2. Listar Personas      ║");
			System.out.println("║  3. Eliminar Personas    ║");
			System.out.println("║  4. Filtros de Personas  ║");
			System.out.println("╠══════════════════════════╣");
			System.out.println("║  0. Volver al Menú       ║");
			System.out.println("╚══════════════════════════╝");
			System.out.print("Seleccione una opción: ");
			opcion = scanner.nextInt();
			scanner.nextLine(); // Limpiar buffer

			try {
				switch (opcion) {
				case 1:
					String driverID;
					do {
						driverID = LibIO.solicitarString("Introduzca el Id del conductor o 0 para salir", 0, 50);
						if (driverID.equals("0")) {
							break;
						}
						String address = LibIO.solicitarString("Introduzca la direccion", 0, 50);
						String name = LibIO.solicitarString("Introduzca el nombre del conductor", 0, 50);
						appService.addPerson(driverID, address, name);
						System.out.println("Persona añadida correctamente.");
					} while (true);
					break;
				case 2:
					appService.getAllPersons().forEach(System.out::println);
					break;
				case 3:
					// TODO: Delete person
					break;
				case 4:
					// TODO: Person Filters
					break;
				case 0:
					break;
				default:
					System.out.println("Opción no válida.");
				}
			} catch (DatabaseException e) {
				System.err.println("Error: " + e.getMessage());
			}
		} while (opcion != 0);
	}

	private void gestionarCoches() throws Exception {
		int opcion;
		do {
			System.out.println();
			System.out.println("╔══════════════════════════╗");
			System.out.println("║     GESTIÓN DE COCHES    ║");
			System.out.println("╠══════════════════════════╣");
			System.out.println("║  1. Añadir Coche         ║");
			System.out.println("║  2. Listar Coches        ║");
			System.out.println("║  3. Eliminar Coches      ║");
			System.out.println("║  4. Filtros de Coches    ║");
			System.out.println("╠══════════════════════════╣");
			System.out.println("║  0. Volver al Menú       ║");
			System.out.println("╚══════════════════════════╝");
			System.out.print("Seleccione una opción: ");
			opcion = scanner.nextInt();
			scanner.nextLine(); // Limpiar buffer

			try {
				switch (opcion) {
				case 1:
					String licenseId;
					do {
						licenseId = LibIO.solicitarString("Introduzca el Id del coche o 0 para salir", 0, 50);

						if (licenseId.equals("0")) {
							break;
						}

						try {
							String model = LibIO.solicitarString("Modelo", 0, 50);
							if (model.trim().isEmpty()) {
								System.err.println("El modelo no puede estar vacío");
								continue;
							}

							Integer year = LibIO.solicitarInt("Año", 0, 2025);
							String driverId = LibIO.solicitarString("ID del propietario: ", 0, 20);

							appService.addCar(licenseId, model, year, driverId);
							System.out.println("Coche añadido correctamente.");

						} catch (Exception e) {
							System.err.println("Error al añadir el coche: " + e.getMessage());
							System.out.println("Por favor, intente nuevamente.");
						}
					} while (true);
					break;
				case 2:
					appService.getAllCars().forEach(System.out::println);
					break;
				case 3:
					// TODO: Delete car
					break;
				case 4:
					// TODO: Car Filters
					break;
				case 0:
					break;
				default:
					System.out.println("Opción no válida.");
				}
			} catch (DatabaseException e) {
				System.err.println("Error: " + e.getMessage());
			}
		} while (opcion != 0);
	}

	private void gestionarPolizas() throws Exception {
		int opcion;

		do {
			System.out.println();
			System.out.println("╔══════════════════════════╗");
			System.out.println("║    GESTIÓN DE PÓLIZAS    ║");
			System.out.println("╠══════════════════════════╣");
			System.out.println("║  1. Añadir Póliza        ║");
			System.out.println("║  2. Listar Pólizas       ║");
			System.out.println("║  3. Eliminar Pólizas     ║");
			System.out.println("║  4. Filtros de Pólizas   ║");
			System.out.println("╠══════════════════════════╣");
			System.out.println("║  0. Volver al Menú       ║");
			System.out.println("╚══════════════════════════╝");
			System.out.print("Seleccione una opción: ");
			opcion = scanner.nextInt();
			scanner.nextLine(); // Limpiar buffer

			try {
				switch (opcion) {
				case 1:
					do {
						String policyID = LibIO.solicitarString("Introduzca el Id de poliza o 0 para salir", 0, 50);
						if (policyID.equals("0")) {
							break;
						}
						try {
							String licenseID = LibIO.solicitarString("Introduzca el Id del coche", 0, 50);
							if (licenseID.trim().isEmpty()) {
								System.err.println("El Id del coche no puede ser nulo");
								continue;
							}
							appService.addPolicy(policyID, licenseID);
							System.out.println("Póliza añadida correctamente.");
						} catch (Exception e) {
							System.err.println("Error al añadir la poliza: " + e.getMessage());
							System.out.println("Por favor, intente nuevamente.");
						}
					}

					while (true);
					break;
				case 2:
					appService.getAllPolicies().forEach(System.out::println);
					break;
				case 3:
					// TODO: Delete policy
					break;
				case 4:
					// TODO: Policy Filters
					break;
				case 0:
					break;
				default:
					System.out.println("Opción no válida.");
				}
			} catch (DatabaseException e) {
				System.err.println("Error: " + e.getMessage());
			}
		} while (opcion != 0);
	}

	private void gestionarAccidentes() {
		int opcion;
		do {

			System.out.println();
			System.out.println("╔══════════════════════════╗");
			System.out.println("║  GESTIÓN DE ACCIDENTES   ║");
			System.out.println("╠══════════════════════════╣");
			System.out.println("║  1. Añadir Accidente     ║");
			System.out.println("║  2. Listar Accidentes    ║");
			System.out.println("║  3. Eliminar Accidentes  ║");
			System.out.println("║  4. Filtros de Accidentes║");
			System.out.println("╠══════════════════════════╣");
			System.out.println("║  0. Volver al Menú       ║");
			System.out.println("╚══════════════════════════╝");
			System.out.print("Seleccione una opción: ");
			opcion = scanner.nextInt();
			scanner.nextLine(); // Limpiar buffer

			try {
				switch (opcion) {
				case 1:
					String reportNumber = LibIO.solicitarString("Número de reporte:", 0, 50);
					String location = LibIO.solicitarString("Ubicación:", 0, 50);
					String licenseId = LibIO.solicitarString("Introduzca el id del coche accidentado", 0, 50);
					appService.addAccident(reportNumber, location);
					appService.addCarAccident(licenseId, reportNumber);
					System.out.println("Accidente añadido correctamente.");
					break;
				case 2:
					appService.getAllAccidents().forEach(System.out::println);
					break;
				case 3:
					// TODO: Delete accident
					break;
				case 4:
					// TODO: Accident Filters
					break;
				case 0:
					break;
				default:
					System.out.println("Opción no válida.");
				}
			} catch (DatabaseException e) {
				System.err.println("Error: " + e.getMessage());
			}
		} while (opcion != 0);
	}

	private void filterMenu() {

	}
}