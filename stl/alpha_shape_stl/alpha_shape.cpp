/*

Source (inspiration):
http://stackoverflow.com/questions/24682250/creating-3d-alpha-shapes-in-cgal-and-the-visualization?lq=1

*/

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Delaunay_triangulation_3.h>
#include <CGAL/Alpha_shape_3.h>

#include <iostream>
#include <fstream>
#include <list>
#include <cassert>
#include <map>

typedef CGAL::Exact_predicates_inexact_constructions_kernel Gt;

typedef CGAL::Alpha_shape_vertex_base_3<Gt>          Vb;
typedef CGAL::Alpha_shape_cell_base_3<Gt>            Fb;
typedef CGAL::Triangulation_data_structure_3<Vb,Fb>  Tds;
typedef CGAL::Delaunay_triangulation_3<Gt,Tds>       Triangulation_3;
typedef CGAL::Alpha_shape_3<Triangulation_3>         Alpha_shape_3;

typedef Alpha_shape_3::Facet                          Facet;
typedef Alpha_shape_3::Cell_handle                    Cell_handle;

typedef Gt::Point_3                                  Point;
typedef Alpha_shape_3::Alpha_iterator               Alpha_iterator;

using namespace std;
int main(int argc, char* argv[])
{
  std::list<Point> lp;
  map<Point, int> pMap;

  //read input
  if (argc <= 2) {
      std::cout << "Usage: alpha_shape <point_file> <new_file> [alpha]" << std::endl;
      std::cout << "If alpha is not provided, optimal alpha is calculated" << std::endl;
      std::cout << "Point file should start with a header line with the total ";
      std::cout << "number of points. The new file will be a list of indices (int) ";
      std::cout << "with reference to the points in the point file." << std::endl;
      return 0;
  }
  const char* filename = argv[1];
  const char* new_filename = argv[2];
  std::ifstream is(filename);
  int n;
  is >> n;
  std::cout << "Reading " << n << " points " << std::endl;
  Point p;
  for(int i = 0 ; n>0 ; n--)    {
    is >> p;
    lp.push_back(p);
    pMap[p] = i;
    i++;    
  }

  // compute alpha shape
//  Alpha_shape_3 as(lp.begin(),lp.end());
  Alpha_shape_3 as(lp.begin(),lp.end(),0.001, Alpha_shape_3::GENERAL);

  // find optimal alpha value
  Alpha_iterator opt = as.find_optimal_alpha(1);
  std::cout << "Optimal alpha value to get one connected component is "
      <<  *opt    << std::endl;
  as.set_alpha(*opt);
  assert(as.number_of_solid_components() == 1);
  
  if (argc >= 4) {
    std::cout << "Using alpha = " << atof(argv[3]) << std::endl;
    as.set_alpha(atof(argv[3]));
    std::cout << "Number of solids components: " << as.number_of_solid_components() << std::endl;
  }
  
  std::stringstream ind;
  
  std::list<Facet> facets;
  as.get_alpha_shape_facets(std::back_inserter(facets), Alpha_shape_3::REGULAR);
  as.get_alpha_shape_facets(std::back_inserter(facets), Alpha_shape_3::SINGULAR);
   for(std::list<Facet>::const_iterator iter = facets.begin(); iter != facets.end(); iter++) {
        
        const Cell_handle& ch = iter->first;
        const int index = iter->second;

        const Point& a = ch->vertex((index+1)&3)->point();
        const Point& b = ch->vertex((index+2)&3)->point();
        const Point& c = ch->vertex((index+3)&3)->point();
        
        ind << pMap[a] << " ";
        ind << pMap[b] << " ";
        ind << pMap[c] << "\n";
        
    }

  ofstream indfile;
  indfile.open (new_filename);
  //indfile << "p0 p1 p2\n";
  indfile << ind.str();
  indfile.close();
  
  return 0;
}
