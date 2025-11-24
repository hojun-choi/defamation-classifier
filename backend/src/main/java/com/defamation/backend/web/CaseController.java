package com.defamation.backend.web;

import com.defamation.backend.repository.CaseRepository;
import com.defamation.backend.web.dto.CaseDto;
import com.defamation.backend.web.dto.PageResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/cases")
@RequiredArgsConstructor
public class CaseController {

    private final CaseRepository caseRepository;
    private final ObjectMapper om = new ObjectMapper();

    // GET /api/cases?q=키워드&page=0&size=10
    @GetMapping
    public PageResponse<CaseDto> list(
            @RequestParam(required = false) String q,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        Pageable pageable = PageRequest.of(page, size);
        Page<CaseDto> result = caseRepository.search(q, pageable)
                .map(c -> CaseDto.from(c, om));

        return PageResponse.<CaseDto>builder()
                .items(result.getContent())
                .page(page)
                .size(size)
                .totalElements(result.getTotalElements())
                .totalPages(result.getTotalPages())
                .build();
    }
}
