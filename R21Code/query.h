#ifndef analysis_query_H
#define analysis_query_H


// TODO: Clean up all the C++ code so it looks "nice"

#include <AnaAlgorithm/AnaAlgorithm.h>

class query : public EL::AnaAlgorithm
{
public:
  // this is a standard algorithm constructor
  query (const std::string& name, ISvcLocator* pSvcLocator);

  // these are the functions inherited from Algorithm
  virtual StatusCode initialize () override;
  virtual StatusCode execute () override;
  virtual StatusCode finalize () override;

private:
  {% for l in class_dec %}
  {{l}}
  {% endfor %}

};

#endif